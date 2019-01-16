import com.github.yuiskw.beam.BigQuery2Datastore;

import java.io.IOException;
import java.util.ArrayList;
import javax.servlet;

public class Dataflow {
    public static void main(String[] args) throws Exception {
//        ArrayList<String> params = new ArrayList<String>() {{
//            add("com.github.yuiskw.beam.BigQuery2Datastore");
//            add("--project=data-streamwise");
//            add("--runner=DataflowRunner");
//            add("--inputBigQueryDataset=street_traffic");
//            add("--inputBigQueryTable=da" +
//                    "ily_traffic_10mins");
//            add("--outputDatastoreNamespace=default");
//            add("--outputDatastoreKind=daily_traffic");
//            add("--keyColumn=id");
//            add("--indexedColumns=id,_description,_east,_last_updt,_north,_region_id,_south,_west,current_speed,region");
//            add(" --tempLocation=gs://streamwise/tmp/");
//            add("--gcpTempLocation=gs://streamwise/logs/");
//        }};

        BigQuery2Datastore.main(new String[]{
                "--project=data-streamwise",
                "--runner=DataflowRunner",
                "--inputBigQueryDataset=street_traffic",
                "--inputBigQueryTable=daily_traffic_10mins",
                "--outputDatastoreNamespace=default",
                "--outputDatastoreKind=daily_traffic",
                "--keyColumn=id",
                "--indexedColumns=id,_description,_east,_last_updt,_north,_region_id,_south,_west,current_speed,region",
                "--tempLocation=gs://streamwise/tmp/",
                "--gcpTempLocation=gs://streamwise/logs/"
        });

        // new main.appengine.JarExecutor().executeJar("/Users/gbenga/Downloads/gcloud/data_streamwise/data_flow/bigquery-to-datastore/out/artifacts/bigquery_to_datastore_jar/bigquery_to_datastore.jar",params);


    }
}