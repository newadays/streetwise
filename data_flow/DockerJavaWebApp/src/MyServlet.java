import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;

import com.github.yuiskw.beam.BigQuery2Datastore;

public class MyServlet extends javax.servlet.http.HttpServlet {


    public void doGet(HttpServletRequest req, HttpServletResponse response) throws IOException {
//        response.setContentType("text/html");
//        response.setCharacterEncoding("UTF-8");
        BigQuery2Datastore.main(new String[]{"--project=data-streamwise",
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

//            try (PrintWriter writer = response.getWriter()) {
//            writer.println("<!DOCTYPE html><html>");
//            writer.println("<head>");
//            writer.println("<meta charset=\"UTF-8\" />");
//            writer.println("<title>MyServlet.java:doGet(): Servlet code!</title>");
//            writer.println("</head>");
//            writer.println("<body>");
//
//            writer.println("<h1>This is a simple java servlet.</h1>");
//
//            writer.println("</body>");
//            writer.println("</html>");
//        }
    }
}


//    protected void doPost(javax.servlet.http.HttpServletRequest request, javax.servlet.http.HttpServletResponse response) throws javax.servlet.ServletException, IOException {
//
//    }
//
//    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
//        response.setContentType("text/html");
//        response.setCharacterEncoding("UTF-8");
//
//        try (PrintWriter writer = response.getWriter()) {
//            writer.println("<!DOCTYPE html><html>");
//            writer.println("<head>");
//            writer.println("<meta charset=\"UTF-8\" />");
//            writer.println("<title>MyServlet.java:doGet(): Servlet code!</title>");
//            writer.println("</head>");
//            writer.println("<body>");
//
//            writer.println("<h1>This is a simple java servlet.</h1>");
//
//            writer.println("</body>");
//            writer.println("</html>");
//        }
//    }
//}
