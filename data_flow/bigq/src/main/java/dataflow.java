import com.github.yuiskw.beam.BigQuery2Datastore;

public class dataflow {
    public static void main(String[] args) throws Exception {

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

    }

}