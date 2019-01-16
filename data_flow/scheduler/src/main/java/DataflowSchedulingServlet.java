//@WebServlet(name = "dataflowscheduler", value = "/dataflow/schedule")
//public class DataflowSchedulingServlet extends HttpServlet {
//    @Override
//    public void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
//        ScheduledMinimalWordCount.run();
//    }
//}


import com.github.yuiskw.beam.BigQuery2Datastore;

//import java.io.BufferedReader;
//import java.io.IOException;
//import java.io.InputStreamReader;
//import java.util.ArrayList;
//import java.util.List;

@WebServlet(name = "dataflowscheduler", value = "/dataflow/schedule")
public class DataflowSchedulingServlet extends HttpServlet {
    @Override
    public void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {

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

