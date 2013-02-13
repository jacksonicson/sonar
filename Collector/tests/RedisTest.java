import java.util.ArrayList;
import java.util.List;

import redis.clients.jedis.Jedis;

public class RedisTest {

	public RedisTest() {
		Jedis jedis = new Jedis("srv2");

		// jedis.set("foo", "bar");
		String value = jedis.get("foo");

		System.out.println("Value: " + value);

		value = jedis.get("h/srv2/name");
		System.out.println("Value: " + value);

		List<String> list = new ArrayList<String>();
		list.add("hello");
		list.add("world"); 
		
		String[] ll = new String[list.size()];
		list.toArray(ll);

		jedis.rpush("list", ll);

		long len = jedis.llen("list");
		System.out.println("length: " + len);

		List<String> valuse = jedis.lrange("list", 0, len);

		for (String v : valuse) {
			System.out.println("v: " + v);
		}

		// jedis.set("h/srv2/name", "Server 2 Dell");
		// jedis.set("h/srv2/sensors", "sensor list here");

	}

	public static void main(String arg[]) {
		new RedisTest();
	}

}
