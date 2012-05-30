import java.io.IOException;

import org.apache.hadoop.hbase.client.Delete;
import org.apache.hadoop.hbase.client.Get;
import org.apache.hadoop.hbase.client.HTable;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.ResultScanner;
import org.apache.hadoop.hbase.client.Scan;

import de.tum.in.sonar.collector.HBaseUtil;

public class DeleteCompleteTsdb {

	public DeleteCompleteTsdb() throws IOException {

		HBaseUtil util = new HBaseUtil();

		HTable table = new HTable(util.getConfig(), "tsdb");
		Get get = new Get();

		Scan scan = new Scan();

		ResultScanner scanner = table.getScanner(scan);
		for (Result res : scanner) {

			System.out.println("Deleting row: " + res.getRow());

			Delete delete = new Delete(res.getRow());
			table.delete(delete);
		}

	}

	public static void main(String[] arg) {
		try {
			new DeleteCompleteTsdb();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

}
