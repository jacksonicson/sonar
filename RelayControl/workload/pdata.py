import modifier
from timeutil import * #@UnusedWildImport

class Desc:
    '''
    Describes a single TS which is used to generate a profile
    '''
    def __init__(self, name, profile_set, modifier=modifier.MOD0, scale=(1, 1), shift=0, additive=0):
        self.name = name
        self.sample_frequency = profile_set.ifreq
        self.profile_set = profile_set
        
        self.modifier = modifier
        self.scale = scale 
        self.shift = shift
        self.additive = additive

class ProfileSet:
    '''
    A profile set describes shared properties between sets of TS
    '''
    def __init__(self, sid, ifreq, cap, day=None):
        self.id = sid 
        self.ifreq = ifreq
        self.cap = cap
        self.day = day


# List of profile sets
SET_O2_BUSINESS = ProfileSet(0, hour(1), None)
SET_O2_RETAIL = ProfileSet(1, hour(1), None)
SET_SIS = ProfileSet(2, minu(5), 3000)

# List of profile days
SET_SIS_D3 = ProfileSet(3, minu(5), 3000, day=3)
SET_SIS_D8 = ProfileSet(3, minu(5), 3000, day=8)
SET_SIS_D9 = ProfileSet(3, minu(5), 3000, day=9)
SET_SIS_D10 = ProfileSet(3, minu(5), 3000, day=10)
SET_SIS_D26 = ProfileSet(3, minu(5), 3000, day=26)


# MIX0
mix_0 = [
            Desc('O2_business_ADDORDER', SET_O2_BUSINESS, modifier.MOD8, (1.2, 1), minu(10), 20),
            Desc('O2_business_SENDMSG', SET_O2_BUSINESS, modifier.MOD2, (1.1, 1), minu(-15), 20),
            Desc('O2_business_UPDATEACCOUNT', SET_O2_BUSINESS, modifier.MOD3, (1.3, 1.1), minu(10), 20),
            Desc('O2_retail_ADDORDER', SET_O2_RETAIL, modifier.MOD8, (1, 0.8), minu(30), 10),
            Desc('SIS_161_cpu', SET_SIS, modifier.MOD5, (1.1, 0.9), minu(10), 5),
            Desc('SIS_162_cpu', SET_SIS, modifier.MOD7, (1, 1), minu(15), 20),
            Desc('SIS_163_cpu', SET_SIS, modifier.MOD1, (1, 1.3), minu(0), 20),
            Desc('SIS_175_cpu', SET_SIS, modifier.MOD2, (1.1, 1), minu(-5), 20),
            Desc('SIS_177_cpu', SET_SIS, modifier.MOD8, (1, 1), minu(20), 20),
            Desc('SIS_179_cpu', SET_SIS, modifier.MOD4, (1, 1), minu(-7), 20),
            Desc('SIS_188_cpu', SET_SIS, modifier.MOD5, (1, 1), minu(0), 20),
            Desc('SIS_269_cpu', SET_SIS, modifier.MOD6, (1, 1.1), minu(1), 20),
            Desc('SIS_298_cpu', SET_SIS, modifier.MOD7, (1.1, 1), minu(0), 20),
            Desc('SIS_305_cpu', SET_SIS, modifier.MOD1, (1, 1), minu(-6), 20),
            Desc('SIS_308_cpu', SET_SIS, modifier.MOD7, (1, 1), minu(5), 20),
            Desc('SIS_310_cpu', SET_SIS, modifier.MOD3, (1, 0.9), minu(10), 20),
            Desc('SIS_340_cpu', SET_SIS, modifier.MOD4, (1, 1), minu(15), 20),
            Desc('SIS_393_cpu', SET_SIS, modifier.MOD3, (1.1, 1), minu(0), 20),
            Desc('SIS_397_cpu', SET_SIS, modifier.MOD7, (1.05, 1.1), minu(-10), 20),
            Desc('SIS_29_cpu', SET_SIS_D3, modifier.MOD8, (1, 1), minu(20), 30),
            ]

# MIX1
mix_1 = [
         Desc('SIS_397_cpu', SET_SIS, modifier.MOD7, (1.1, 1), minu(10), 30),
         Desc('SIS_199_cpu', SET_SIS_D8, modifier.MOD7, (1.1, 0.9), minu(-5), 50),
         Desc('SIS_207_cpu', SET_SIS_D9, modifier.MOD4, (1.1, 1), minu(-30), 50),
         Desc('SIS_211_cpu', SET_SIS_D9, modifier.MOD0, (1.2, 0.8), minu(10), 50),
         Desc('SIS_213_cpu', SET_SIS_D9, modifier.MOD5, (1, 1.1), minu(20), 30),
         Desc('SIS_216_cpu', SET_SIS_D9, modifier.MOD5, (1.2, 1), minu(0), 20),
         Desc('SIS_221_cpu', SET_SIS_D9, modifier.MOD7, (1, 1.3), minu(-10), 30),
         Desc('SIS_222_cpu', SET_SIS_D9, modifier.MOD1, (1.0, 1), minu(-50), 30),
         Desc('SIS_225_cpu', SET_SIS_D9, modifier.MOD9, (1.1, 1.3), minu(10), 10),
         Desc('SIS_234_cpu', SET_SIS_D9, modifier.MOD8, (1, 1), minu(50), 40),
         Desc('SIS_245_cpu', SET_SIS_D9, modifier.MOD4, (1.1, 1), minu(0), 20),
         Desc('SIS_264_cpu', SET_SIS_D9, modifier.MOD3, (1, 1), minu(-20), 50),
         Desc('SIS_271_cpu', SET_SIS_D9, modifier.MOD6, (1.1, 1.4), minu(50), 40),
         Desc('SIS_275_cpu', SET_SIS_D9, modifier.MOD5, (1.02, 1.3), minu(15), 10),
         Desc('SIS_279_cpu', SET_SIS_D9, modifier.MOD1, (1.2, 1), minu(30), 10),
         Desc('SIS_344_cpu', SET_SIS_D8, modifier.MOD2, (1.05, 1), minu(6), 30),
         Desc('SIS_345_cpu', SET_SIS_D8, modifier.MOD0, (1.3, 1.1), minu(-100), 30),
         Desc('SIS_350_cpu', SET_SIS_D8, modifier.MOD8, (1, 1), minu(0), 10),
         Desc('SIS_385_cpu', SET_SIS_D9, modifier.MOD3, (1.03, 1.4), minu(10), 20),
         Desc('SIS_387_cpu', SET_SIS_D9, modifier.MOD6, (1.1, 1.7), minu(50), 50),
         ]

# MIX2
mix_2 = [
         Desc('O2_business_ADDORDER', SET_O2_BUSINESS, modifier.MOD1, (1, 1), minu(10), 20),
         Desc('O2_business_SENDMSG', SET_O2_BUSINESS, modifier.MOD7, (1, 1), minu(-5), 20),
         Desc('O2_business_UPDATEACCOUNT', SET_O2_BUSINESS, modifier.MOD8, (1.1, 1), minu(20), 20),
         Desc('SIS_163_cpu', SET_SIS, modifier.MOD4, (1, 1), minu(10), 20),
         Desc('SIS_175_cpu', SET_SIS, modifier.MOD5, (1, 1.1), minu(-20), 20),
         Desc('SIS_179_cpu', SET_SIS, modifier.MOD6, (1, 1), minu(-10), 20),
         Desc('SIS_298_cpu', SET_SIS, modifier.MOD7, (1, 1), minu(0), 20),
         Desc('SIS_310_cpu', SET_SIS, modifier.MOD8, (1.2, 1), minu(0), 10),
         Desc('SIS_340_cpu', SET_SIS, modifier.MOD2, (1, 1), minu(5), 10),
         Desc('SIS_29_cpu', SET_SIS_D3, modifier.MOD3, (1, 1.2), hour(1), 20),
         Desc('SIS_199_cpu', SET_SIS_D8, modifier.MOD4, (1, 1), minu(10), 20),
         Desc('SIS_211_cpu', SET_SIS_D9, modifier.MOD4, (1.03, 1.1), minu(0), 20),
         Desc('SIS_216_cpu', SET_SIS_D9, modifier.MOD7, (1.1, 1), minu(20), 0),
         Desc('SIS_225_cpu', SET_SIS_D9, modifier.MOD7, (1.3, 1), minu(-15), 20),
         Desc('SIS_234_cpu', SET_SIS_D9, modifier.MOD1, (1.4, 1.2), minu(0), 20),
         Desc('SIS_264_cpu', SET_SIS_D9, modifier.MOD2, (1, 1), minu(10), 10),
         Desc('SIS_279_cpu', SET_SIS_D9, modifier.MOD0, (1.2, 1), minu(20), 40),
         Desc('SIS_345_cpu', SET_SIS_D8, modifier.MOD8, (1, 1.5), minu(0), 40),
         Desc('SIS_387_cpu', SET_SIS_D9, modifier.MOD4, (1.3, 1), minu(15), 20),
         Desc('SIS_199_cpu', SET_SIS_D8, modifier.MOD7, (1.1, 1), minu(0), 20),
         ]

# MIX Simulation
mix_sim = [
            Desc('O2_business_ADDORDER', SET_O2_BUSINESS, modifier.MOD8, (1.2, 1), minu(10), 20),
            Desc('O2_business_ADDLINEORDER', SET_O2_BUSINESS),
            Desc('O2_business_CONTRACTEXT', SET_O2_BUSINESS),
            Desc('O2_business_SENDMSG', SET_O2_BUSINESS),
            Desc('O2_business_UPDATEACCOUNT', SET_O2_BUSINESS),
            Desc('O2_business_UPDATEDSS', SET_O2_BUSINESS),
            
            Desc('O2_retail_ADDORDER', SET_O2_RETAIL),
            Desc('O2_retail_CONTRACTEXT', SET_O2_RETAIL),
            Desc('O2_retail_ADDUCP', SET_O2_RETAIL),
            Desc('O2_retail_SENDMSG', SET_O2_RETAIL),
            Desc('O2_retail_UPDATEACCOUNT', SET_O2_RETAIL),
            Desc('O2_retail_UPDATEDSS', SET_O2_RETAIL),
            
            Desc('SIS_161_cpu', SET_SIS),
            Desc('SIS_162_cpu', SET_SIS),
            Desc('SIS_163_cpu', SET_SIS),
            Desc('SIS_172_cpu', SET_SIS),
            Desc('SIS_175_cpu', SET_SIS),
            Desc('SIS_177_cpu', SET_SIS),
            Desc('SIS_178_cpu', SET_SIS),
            Desc('SIS_179_cpu', SET_SIS),
            Desc('SIS_188_cpu', SET_SIS),
            Desc('SIS_189_cpu', SET_SIS),
            Desc('SIS_198_cpu', SET_SIS),
            Desc('SIS_194_cpu', SET_SIS),
            Desc('SIS_209_cpu', SET_SIS),
            Desc('SIS_240_cpu', SET_SIS),
            Desc('SIS_253_cpu', SET_SIS),
            Desc('SIS_269_cpu', SET_SIS),
            Desc('SIS_292_cpu', SET_SIS),
            Desc('SIS_298_cpu', SET_SIS),
            Desc('SIS_305_cpu', SET_SIS),
            Desc('SIS_308_cpu', SET_SIS),
            Desc('SIS_309_cpu', SET_SIS),
            Desc('SIS_310_cpu', SET_SIS),
            Desc('SIS_313_cpu', SET_SIS),
            Desc('SIS_314_cpu', SET_SIS),
            Desc('SIS_340_cpu', SET_SIS),
            Desc('SIS_374_cpu', SET_SIS),
            Desc('SIS_393_cpu', SET_SIS),
            Desc('SIS_394_cpu', SET_SIS),
            Desc('SIS_397_cpu', SET_SIS),
            
            Desc('SIS_21_cpu', SET_SIS_D3),
            Desc('SIS_24_cpu', SET_SIS_D3),
            Desc('SIS_27_cpu', SET_SIS_D3),
            Desc('SIS_29_cpu', SET_SIS_D3),
            Desc('SIS_31_cpu', SET_SIS_D3),
            Desc('SIS_110_cpu', SET_SIS_D3),
            Desc('SIS_145_cpu', SET_SIS_D3),
            Desc('SIS_147_cpu', SET_SIS_D3),
            Desc('SIS_150_cpu', SET_SIS_D3),
            Desc('SIS_162_cpu', SET_SIS_D3),
            Desc('SIS_209_cpu', SET_SIS_D3),
            Desc('SIS_210_cpu', SET_SIS_D3),
            Desc('SIS_236_cpu', SET_SIS_D3),
            Desc('SIS_243_cpu', SET_SIS_D3),
            Desc('SIS_252_cpu', SET_SIS_D3),
            Desc('SIS_253_cpu', SET_SIS_D3),
            Desc('SIS_272_cpu', SET_SIS_D3),
            Desc('SIS_373_cpu', SET_SIS_D3),
            
            Desc('SIS_29_cpu', SET_SIS_D8),
            Desc('SIS_31_cpu', SET_SIS_D8),
            Desc('SIS_123_cpu', SET_SIS_D8),
            Desc('SIS_124_cpu', SET_SIS_D8),
            Desc('SIS_125_cpu', SET_SIS_D8),
            Desc('SIS_145_cpu', SET_SIS_D8),
            Desc('SIS_147_cpu', SET_SIS_D8),
            Desc('SIS_148_cpu', SET_SIS_D8),
            Desc('SIS_149_cpu', SET_SIS_D8),
            Desc('SIS_192_cpu', SET_SIS_D8),
            Desc('SIS_199_cpu', SET_SIS_D8),
            Desc('SIS_211_cpu', SET_SIS_D8),
            Desc('SIS_283_cpu', SET_SIS_D8),
            Desc('SIS_337_cpu', SET_SIS_D8),
            Desc('SIS_344_cpu', SET_SIS_D8),
            Desc('SIS_345_cpu', SET_SIS_D8),
            Desc('SIS_350_cpu', SET_SIS_D8),
            Desc('SIS_352_cpu', SET_SIS_D8),
            Desc('SIS_354_cpu', SET_SIS_D8),
            Desc('SIS_357_cpu', SET_SIS_D8),
            Desc('SIS_383_cpu', SET_SIS_D8),
            
            Desc('SIS_207_cpu', SET_SIS_D9),
            Desc('SIS_208_cpu', SET_SIS_D9),
            Desc('SIS_210_cpu', SET_SIS_D9),
            Desc('SIS_211_cpu', SET_SIS_D9),
            Desc('SIS_213_cpu', SET_SIS_D9),
            Desc('SIS_214_cpu', SET_SIS_D9),
            Desc('SIS_216_cpu', SET_SIS_D9),
            Desc('SIS_219_cpu', SET_SIS_D9),
            Desc('SIS_220_cpu', SET_SIS_D9),
            Desc('SIS_221_cpu', SET_SIS_D9),
            Desc('SIS_222_cpu', SET_SIS_D9),
            Desc('SIS_223_cpu', SET_SIS_D9),
            Desc('SIS_225_cpu', SET_SIS_D9),
            Desc('SIS_234_cpu', SET_SIS_D9),
            Desc('SIS_235_cpu', SET_SIS_D9),
            Desc('SIS_243_cpu', SET_SIS_D9),
            Desc('SIS_245_cpu', SET_SIS_D9),
            Desc('SIS_264_cpu', SET_SIS_D9),
            Desc('SIS_269_cpu', SET_SIS_D9),
            Desc('SIS_270_cpu', SET_SIS_D9),
            Desc('SIS_271_cpu', SET_SIS_D9),
            Desc('SIS_275_cpu', SET_SIS_D9),
            Desc('SIS_279_cpu', SET_SIS_D9),
            Desc('SIS_312_cpu', SET_SIS_D9),
            Desc('SIS_315_cpu', SET_SIS_D9),
            Desc('SIS_328_cpu', SET_SIS_D9),
            Desc('SIS_385_cpu', SET_SIS_D9),
            Desc('SIS_386_cpu', SET_SIS_D9),
            Desc('SIS_387_cpu', SET_SIS_D9),
            
            Desc('SIS_207_cpu', SET_SIS_D10),
            Desc('SIS_208_cpu', SET_SIS_D10),
            Desc('SIS_210_cpu', SET_SIS_D10),
            Desc('SIS_211_cpu', SET_SIS_D10),
            Desc('SIS_213_cpu', SET_SIS_D10),
            Desc('SIS_214_cpu', SET_SIS_D10),
            Desc('SIS_216_cpu', SET_SIS_D10),
            Desc('SIS_219_cpu', SET_SIS_D10),
            Desc('SIS_220_cpu', SET_SIS_D10),
            Desc('SIS_221_cpu', SET_SIS_D10),
            Desc('SIS_222_cpu', SET_SIS_D10),
            Desc('SIS_223_cpu', SET_SIS_D10),
            Desc('SIS_225_cpu', SET_SIS_D10),
            Desc('SIS_234_cpu', SET_SIS_D10),
            Desc('SIS_235_cpu', SET_SIS_D10),
            Desc('SIS_243_cpu', SET_SIS_D10),
            Desc('SIS_245_cpu', SET_SIS_D10),
            Desc('SIS_264_cpu', SET_SIS_D10),
            Desc('SIS_269_cpu', SET_SIS_D10),
            Desc('SIS_270_cpu', SET_SIS_D10),
            Desc('SIS_271_cpu', SET_SIS_D10),
            Desc('SIS_275_cpu', SET_SIS_D10),
            Desc('SIS_279_cpu', SET_SIS_D10),
            Desc('SIS_312_cpu', SET_SIS_D10),
            Desc('SIS_315_cpu', SET_SIS_D10),
            Desc('SIS_328_cpu', SET_SIS_D10),
            Desc('SIS_385_cpu', SET_SIS_D10),
            Desc('SIS_386_cpu', SET_SIS_D10),
            Desc('SIS_387_cpu', SET_SIS_D10),
            
            Desc('SIS_21_cpu', SET_SIS_D26),
            Desc('SIS_24_cpu', SET_SIS_D26),
            Desc('SIS_27_cpu', SET_SIS_D26),
            Desc('SIS_29_cpu', SET_SIS_D26),
            Desc('SIS_31_cpu', SET_SIS_D26),
            Desc('SIS_110_cpu', SET_SIS_D26),
            Desc('SIS_145_cpu', SET_SIS_D26),
            Desc('SIS_147_cpu', SET_SIS_D26),
            Desc('SIS_150_cpu', SET_SIS_D26),
            Desc('SIS_162_cpu', SET_SIS_D26),
            Desc('SIS_209_cpu', SET_SIS_D26),
            Desc('SIS_210_cpu', SET_SIS_D26),
            Desc('SIS_236_cpu', SET_SIS_D26),
            Desc('SIS_243_cpu', SET_SIS_D26),
            Desc('SIS_252_cpu', SET_SIS_D26),
            Desc('SIS_253_cpu', SET_SIS_D26),
            Desc('SIS_272_cpu', SET_SIS_D26),
            Desc('SIS_373_cpu', SET_SIS_D26),
            
            Desc('SIS_298_cpu', SET_SIS),
            Desc('SIS_305_cpu', SET_SIS),
            Desc('SIS_303_cpu', SET_SIS),
            Desc('SIS_309_cpu', SET_SIS),
            Desc('SIS_210_cpu', SET_SIS),
            Desc('SIS_213_cpu', SET_SIS),
            Desc('SIS_314_cpu', SET_SIS),
            Desc('SIS_240_cpu', SET_SIS),
            Desc('SIS_374_cpu', SET_SIS),
            Desc('SIS_393_cpu', SET_SIS),
            Desc('SIS_294_cpu', SET_SIS),
            Desc('SIS_197_cpu', SET_SIS),
            
            Desc('O2_business_ADDORDER', SET_O2_BUSINESS, modifier.MOD3, (1.2, 1), minu(10), 20),
            Desc('O2_business_ADDLINEORDER', SET_O2_BUSINESS, modifier.MOD1),
            Desc('O2_business_CONTRACTEXT', SET_O2_BUSINESS, modifier.MOD3),
            Desc('O2_business_SENDMSG', SET_O2_BUSINESS, modifier.MOD2),
            Desc('O2_business_UPDATEACCOUNT', SET_O2_BUSINESS, modifier.MOD4),
            Desc('O2_business_UPDATEDSS', SET_O2_BUSINESS, modifier.MOD3),
           ]