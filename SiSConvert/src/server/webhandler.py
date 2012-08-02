# coding=CP1252

from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from wtforms import Form, TextField, PasswordField, validators, RadioField, \
    BooleanField, HiddenField, FloatField
import calculations
import configuration
import entities
import hashlib
import logging as logger
import simplejson as json
import storage
import templating
import time
import tornado
import urlconfig as urls
import work
from datetime import timedelta
from datetime import datetime
import mail
from pymongo import objectid
import uuid
import re

controller = work.Controller()

class BaseHandler(tornado.web.RequestHandler):
    
    def _generate_session_id(self):
        return uuid.uuid1()
    
    def get_current_user(self):
        username = self.get_secure_cookie('user')
        if username is not None:
            user = storage.find_user(username)
            if user is None:
                return None
            
        return username 
    

    def get_current_user_id(self):
        return self.get_secure_cookie('userid')

    # TODO: Remove this
    def _get_arguments_dict(self, arguments=None):
        if arguments is None:
            arguments = self.request.arguments

        arguments_dict = {}
        for arg in arguments:
            arguments_dict[arg] = arguments[arg][0]

        return arguments_dict
    
    
    def _render_error(self, view, msg, params={}):
        params.update({'error' : msg})  
        self.template(view, params)

    
    def template_string(self, template_path, template_dict={}):
        # Add some settings which are user specific
        template_dict.update({'current_user' : self.get_current_user()})
        return templating.process_file(self.render_string, template_path, template_dict)
    
    def template(self, template_path, template_dict={}):
        # Add some settings which are user specific
        template_dict.update({'current_user' : self.get_current_user()})
        
        templating.process_file(self.process_file, template_path, template_dict)


class Root(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # Directly send the user to the dashboard
        self.redirect('/dashboard')
          
          
class SmartCoin(BaseHandler):
    def get(self):
        self.template('smartcoin')

            
class Login(BaseHandler):
    
    class LoginForm(Form):
        user = TextField('Username: ', validators = [validators.required(message='Username is required')])
        pwd = PasswordField('Password: ', validators = [validators.required(message='Password is required')])
        type = RadioField('', choices=[('exists', 'You already have an account'),
                                           ('new', 'Create a new account')], default='exists')
    
    
    def get(self):
        # If the user is logged in, redirect to the dashboard 
        if self.get_current_user():
            self.redirect(urls.ROOT.DASHBOARD.url())
            return
        
        form = self.LoginForm()
        params = {
                  'form' : form,
                  }
        
        # Render the login view
        self.template('login', params)
            
            
    def post(self):
        form = self.LoginForm(**self._get_arguments_dict())
        
        params = {'form' : form} 
        
        # Check the login mode
        p_type = form.type.data
        if p_type == 'new':
            self.redirect(urls.ROOT.REGISTER.url())
        else:
            if form.validate() is False:
                logger.error('form validation for login form failed')
                self.template('login', params)
                return
            
            # Check user
            p_username = form.user.data
            user = storage.find_user(p_username)
            
            # Invalid user
            if user is None:
                logger.debug("user is unkown")
                return self._render_error('login', 'User is unknown', params) 
                
            # Check password
            p_password = form.pwd.data
            m = hashlib.md5()
            m.update(p_password)
            digest_password = m.digest().encode('hex')
            
            if digest_password == user.password and user.account_verification_id == 1:
                logger.debug("valid login") 
                self.set_secure_cookie('user', user.username)
                self.set_secure_cookie('userid', str(user._id))
                self.redirect(urls.ROOT.DASHBOARD.url())
                return
            else:
                logger.debug("invalid login")
                return self._render_error('login', 'Password incorrect or account has not been activated', params)
  
class ResetAccount(BaseHandler):
    class ResetForm(Form):
        mail = TextField('Mail: ', [validators.required(message='Required'),
                                    validators.Regexp('[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}', message='Invalid Email')])
    
    def get(self):
        form = self.ResetForm()
        params = {'form' : form}
        self.template('reset', params)
    
    def post(self):
        form = self.ResetForm(**self._get_arguments_dict())
        params = {'form' : form}
        
        if form.validate() is False:
            logger.debug("Form validation returned false")
            self.template('reset', params)
            return
        
        p_mail = form.mail.data
        
        user = storage.find_user_query({
                                 'mail' : p_mail
                                 })
        
        if user is None: 
            logger.warn("User not found, could not reset password")
            form.mail.errors.append('Unknown email address')
            self.template('reset', params)
            return
            
        
        pwd = controller.generate_user_password()
        user.set_password(pwd)
        storage.save_or_update_user(user)
        
        # Send email with new password
        mail.send_password_reset(user, pwd, self)
        
        # Redirect user to the login
        self.redirect(urls.ROOT.LOGIN.url())
  
class ActivateAccount(BaseHandler):
    def get(self):
        verification_id = self.get_argument('id', None) 
        if verification_id is None:
            logger.error('Could not authenticate user, no ID provided')
            return
        
        user = storage.find_user_query({'account_verification_id' : verification_id})
        if user is None:
            logger.error('Could not find user for verification ID: %s' % verification_id)
            return
        
        logger.info('User activated: %s' % (user.username))
        user.account_verification_id = 1
        storage.save_or_update_user(user)
        
        params = {
                'user' : user,
                }
        
        self.template('activate', params)
        

class Register(BaseHandler):
    
    class RegistrationForm(Form):
        user = TextField('Username: ', [validators.required(message='Required'),
                                        validators.Length(min=5, max=20, message='Invalid length'),
                                        validators.Regexp('[A-Za-z0-9]+', message='Invalid chars')])
        
        pwd0 = PasswordField('Password: ', [validators.required(message='Required'),
                                            validators.Length(min=1, max=20, message='Invalid length')])
        
        pwd1 = PasswordField('Confirm password: ', [validators.required(message='Required'),
                                                    validators.Length(min=1, max=20, message='Invalid length')])
        
        mail = TextField('Mail: ', [validators.required(message='Required'),
                                    validators.Regexp('[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}', message='Invalid Email')])
    
    def get(self):
        form = self.RegistrationForm()
        params = {'form' : form}
        self.template('register', params)
        
    def post(self):
        form = self.RegistrationForm(**self._get_arguments_dict())
        params = {'form' : form}
        
        if form.validate() is False:
            logger.debug("Form validation returned false")
            self.template('register', params)
            return
        
        p_username = form.user.data
        p_pass0 = form.pwd0.data
        p_pass1 = form.pwd1.data
        p_mail = form.mail.data
        
        user = storage.find_user(p_username)
        if user is not None:
            logger.debug("usre already exists")
            self._render_error('register', 'User exists already', params)
            return
        
        if p_pass0 != p_pass1:
            logger.debug("passwords do not match")
            self._render_error('register', 'The provided passwords are inequal', params)
            return

        # Check if email is already taken
        result = storage.find_user_query({'mail' : p_mail})
        if result is not None:
            logger.debug("passwords do not match")
            self._render_error('register', 'The provided email address has already been taken', params)
            return

        m = hashlib.md5()
        m.update(p_pass0)
        digest_password = m.digest().encode('hex')
        
        # Create a new user object
        user = entities.User(p_username, digest_password)
        user.mail = p_mail
        user.account_verification_id = controller.generate_verification_id(user.username)
        storage.save_or_update_user(user)

        # Send verification email
        mail.send_account_verification(user, self)
        
        # Redirect user to the login
        self.template('registerDone', {'email' : user.mail})
        
        
class Logout(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # Remove the secure cookie
        self.set_secure_cookie('user', '')
        self.set_secure_cookie('userid', '')
        self.redirect('/login')


class Account(BaseHandler):

    class Transferable(object):
        def __init__(self):
            self.form = None
            self.payment_form = None
            self.user = None
    
    class AccountForm(Form):
        action = HiddenField('Action', default='user')
        
        pwdc = PasswordField('Current password: ', [validators.Required(message='Required'),
                                                    validators.Length(min=3, max=20, message='Invalid length')])
        
        pwd0 = PasswordField('Password: ', [validators.Length(min=6, max=20, message='Invalid length')])
        
        pwd1 = PasswordField('Confirmation: ', [validators.Length(min=6, max=20, message='Invalid length')])
        
        mail = TextField('Mail: ', [validators.required(message='Required'),
                                    validators.Regexp('[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}', message='Invalid Email')])
        
        mail_miner_defect = BooleanField('Mail on miner defect')

    class PaymentForm(Form):
        action = HiddenField('Action', default='payment')
        
        pwdc = PasswordField('Current password: ', [validators.Required(message='Required'),
                                                    validators.Length(min=3, max=20, message='Invalid length')])
        
        target_wallet = TextField('Target wallet: ', [validators.required(message='Required'),
                                                      validators.Regexp('[A-Za-z0-9]{34}', message='Invalid Wallet')])
        
        threshold = FloatField('Payment threshold: ', [validators.required(message='Required'),
                                                       validators.Regexp('^[0-9]{1,3}(\.[0-9]{1,3})?$', message='Values from 0.0 to 999.999')])
    
    def __fill_user_form(self, form, user):
        form.mail.data = user.mail
        form.mail_miner_defect.data = user.mail_miner_defect
        
    def __fill_payment_form(self, form, user):
        form.target_wallet.data = user.target_wallet
        form.threshold.data = user.threshold
    
    def __construct_transferable(self):
        transferable = self.Transferable()
        transferable.form = self.AccountForm()
        transferable.payment_form = self.PaymentForm()
        
        user = storage.find_user(self.get_current_user())
        transferable.user = user
        
        self.__fill_user_form(transferable.form, user)
        self.__fill_payment_form(transferable.payment_form, user)
        return transferable

    def get(self):
        transferable = self.__construct_transferable()
        param = {'transferable' : transferable}
        self.template('account', param)
        
    def post(self):
        action = self.get_argument('action', '')
        if action == 'user':
            self.__update_user_settings()
        elif action == 'payment':
            self.__update_payment_settings()

    def __update_user_settings(self):
        form = self.AccountForm(**self._get_arguments_dict())
            
        if form.validate() == False:
            logger.debug("Form validation failed")
            transferable = self.__construct_transferable()
            transferable.form = form
            param = {'transferable' : transferable}
            self.template('account', param)
            return
        
        further_errors = False
        
        # Check if passwords match
        if form.pwd0.data != form.pwd1.data and form.pwd0 != None:
            further_errors = True
            form.pwd1.errors.append('Passwords do not match')
            
        user = storage.find_user(self.get_current_user())
        if user.check_password(form.pwdc.data) == False:
            further_errors = True
            form.pwdc.errors.append('Invalid password')
            
        if further_errors:
            transferable = self.__construct_transferable()
            transferable.form = form
            param = {'transferable' : transferable}
            self.template('account', param)
            return

        # Everything seems ok, update user now
        if form.pwd0.data != None:
            user.set_password(form.pwd0.data)
        user.mail = form.mail.data
        user.mail_miner_defect = form.mail_miner_defect.data
        storage.save_or_update_user(user)
         
        return self.get()
        
    
    def __update_payment_settings(self):
        form = self.PaymentForm(**self._get_arguments_dict())
            
        if form.validate() == False:
            logger.debug("Form validation failed")
            transferable = self.__construct_transferable()
            transferable.payment_form = form
            param = {'transferable' : transferable}
            self.template('account', param)
            return
        
        further_errors = False
        
        user = storage.find_user(self.get_current_user())
        if user.check_password(form.pwdc.data) == False:
            further_errors = True
            form.pwdc.errors.append('Invalid password')
            
        if further_errors:
            transferable = self.__construct_transferable()
            transferable.payment_form = form
            param = {'transferable' : transferable}
            self.template('account', param)
            return

        # Everything seems ok, update user now
        user.target_wallet = form.target_wallet.data
        user.threshold = form.threshold.data
        storage.save_or_update_user(user)
         
        return self.get()


class Miners(BaseHandler):
    class Transferable(object):
        def __init__(self):
            self.miners = None

    def __get_miner_template_params(self):
        params = { 
            'configuration' : configuration,
        }
        return params
        
    
    def get(self):
        self.template('miners', self.__get_miner_template_params())
    
    def post(self):
        action = self.get_argument('action', '')
        
        if self.get_argument('action', '') == 'getminers':
            self.__getminers()
        elif self.get_argument('action', '') == 'password':
            self.__generate_password()
        elif self.get_argument('action', '') == 'remove':
            self.__remove_miner()
        elif self.get_argument('action', '') == 'create':
            self.__create_miner()
        elif action == 'loadminer':
            self.__load_miner()
        else:
            self.template('miners', self.__get_miner_template_params())


    def __load_miner(self):
        miner_id = self.get_argument('miner', None)
        oid = objectid.ObjectId(miner_id)
        miner = storage.find_miner(oid)
        
        mining_url = "http://%s%s" % (configuration.get_domain_name(), urls.ROOT.GETWORK.url())
        
        params = self.__get_miner_template_params()
        params['mining_url'] = mining_url
        params['username'] = "%s.%s" % (self.get_current_user(), miner.name)
        params['password'] = miner.password  
        
        self.template('jsminer', params)

    def __create_miner(self):
        user_id = self.get_current_user_id()
        
        miner_name = self.get_argument('name', None)
        
        regexp = '^[a-zA-Z0-9]+$';
        if re.match(regexp, miner_name) is None:
            msg = '{"error": "Invalid chars in name"}'
            self.write(msg)
            return
        
        if miner_name is None or len(miner_name) < 3 or len(miner_name) > 15:
            msg = '{"error": "Length must be 3 to 15 chars"}'
            self.write(msg)
            return 
        
        try:
            controller.create_miner(user_id, miner_name)
        except ValueError:
            msg = '{"error": "Miner with this name already exists"}'
            self.write(msg)
            return
        
        self.write('{"error" : []}')
    

    def __remove_miner(self):
        miner_id = self.get_argument('key')
        controller.remove_miner(miner_id)
        
        self.__getminers()

    def __generate_password(self):
        miner_id = self.get_argument('key')
        
        controller.generate_miner_password(miner_id)
        
        self.__getminers()


    def __getminers(self):
        user = storage.find_user(self.get_current_user())
        miners = controller.get_miners(user._id)
        
        # Update miner object for display
        current_time = time.time()
        for miner in miners:
            miner.last_contact_delta = current_time - miner.last_contact
            miner.last_contact_delta = round(miner.last_contact_delta, 2)
            miner.last_contact_label = 'sec.'
            
            if miner.last_contact_delta > (60): 
                miner.last_contact_delta = round(miner.last_contact_delta / 60, 2)
                miner.last_contact_label = 'min.'
            
            if miner.last_contact_delta > (60): 
                miner.last_contact_delta = round(miner.last_contact_delta / 60, 2)
                miner.last_contact_label = 'h.'
        
        transferable = self.Transferable()
        transferable.miners = miners
        transferable.user = user 
        
        params = {'transferable' : transferable}
        self.template('miner_list', params)


class Payouts(BaseHandler):
    class Transferable(object):
        def __init__(self):
            self.payouts = []
            
    def get(self):
        transferable = self.Transferable(); 
        
        user = storage.find_user(self.get_current_user())
        payouts = storage.find_payouts(user._id)
        transferable.payouts = payouts 
        
        self.template('payouts', {'transferable' : transferable})
        
        

class Blocks(BaseHandler):
    
    class Transferable(object):
        def __init__(self):
            self.blocks = []
    
    def get(self):
        transferable = self.Transferable()
        
        
        pool = storage.get_pool_object()
        
        blocks = storage.find_blocks(pool.current_block, pool.current_block - 100)
        transferable.blocks = blocks
        
        
        self.template('blocks', {'transferable' : transferable})
        
        

class Dashboard(BaseHandler):

    class Transferable(object):
        def __init__(self):
            self.user = None
            self.bitcoin = None
            self.bitcoin_status = False
            self.miners = []
            self.pool = {}

    def __on_response(self, response=None):
        transferable = self.Transferable()

        # Check for errors while communicating with bitcoin
        if response is not None:
            transferable.bitcoin_status = True        
            if response.error is not None:
                logger.error('could not contact bitcoin daemon')
                transferable.bitcoin = None
            else:
                response = json.loads(response.body)
                if response['error'] != None:
                    logger.error("bitcoin daemon returned an error");
                else:
                    transferable.bitcoin = response['result']
            
        # Load current user
        user = storage.find_user(self.get_current_user())
        transferable.user = user

        miners = controller.get_miners(user._id)
        for miner in miners:
            mhash = calculations.calcMinerMhash(miner._id)
            gworks = round(calculations.calc_get_works(miner._id), 2)
            transferable.miners.append((miner.name, mhash, gworks))
            pass 

        
        pool_object = storage.get_pool_object()
        transferable.pool['mhash'] = calculations.calc_pool_mhash()
        transferable.pool['shares_for_current_block'] = calculations.shares_for_current_block(user._id)
        transferable.pool['current_block'] = pool_object.current_block
        transferable.pool['current_difficulty'] = pool_object.current_difficulty
        
        current_block_time = pool_object.current_block_time
        
        td_block_time = timedelta(seconds=current_block_time)
        td_current = timedelta(seconds=time.time())
        td_diff = td_current - td_block_time
        dt_datetime = datetime.fromtimestamp(td_diff.seconds)
        formatted_time_delta = dt_datetime.strftime('%H hours %M minutes %S seconds')
        
        transferable.pool['current_block_time'] = formatted_time_delta  
        
        
        param = {'transferable' : transferable}
        self.template('dashboard', param)
        

    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        self.__on_response()
#        username, password = configuration.get_backend_credentials()
#        
#        url = 'http://' + configuration.get_backend_ip() + ':' + configuration.get_backend_port()
#        http_client = AsyncHTTPClient()
#        request = HTTPRequest(url)
#        request.auth_password = username
#        request.auth_username = password
#        request.method = "POST"
#        request.body = '{"jsonrpc": "2.0", "method": "getinfo"}'
#        http_client.fetch(request, self.__on_response)
