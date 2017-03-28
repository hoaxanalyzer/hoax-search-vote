import org.json.simple.JSONArray;
import org.json.simple.JSONObject;

import java.io.*;
import java.util.*;

/**
 * Created by Tifani on 3/12/2017.
 */
public class HoaxAnalyzer {
    public static final String FEATURE = "feature";
    private static final String COMMAND_PREPROCESS = "preprocess";
    private static final String COMMAND_EXTRACT = "extract";

    public static void createModel() throws IOException {
        String factOrHoax = "fact";
        String dir = "E:\\GitHub\\hoax-analyzer-ml\\dataset\\idn-" + factOrHoax;
        File folder = new File(dir);
        File[] listOfFiles = folder.listFiles();

        String csvFile = "E:\\GitHub\\hoax-analyzer-ml\\idn-" + factOrHoax + ".csv";
        FileWriter writer = new FileWriter(csvFile);

        ArrayList<String> line = new ArrayList<>();
        line.add("filename");
        line.add("text");
        for(int i = 0; i < FeatureExtractor.acceptibleTag.size(); i++) {
            String tag = FeatureExtractor.acceptibleTag.get(i).toLowerCase();
            for(int j = 1; j <= 8; j++) {
                line.add(tag + j + "_token");
                line.add(tag + j + "_prob");
                line.add(tag + j + "_wcount");
                line.add(tag + j + "_wpos");
                line.add(tag + j + "_spos");
            }
            line.add(tag + "_class");
        }
        CSVUtil.writeLine(writer, line);

        for (File file : listOfFiles) {
            if (file.isFile()) {
                String filename = dir + "\\" + file.getName();
                System.out.println(filename);

                String text = HoaxUtil.loadFile(filename);
                HashMap<String, HashMap<String, WordFeature>> wordTag = FeatureExtractor.extractTag(text);
                CSVUtil.writeToCSV(writer, factOrHoax + "-" + file.getName(), text, wordTag);
                System.out.println("done!");
                System.out.println();
            }
        }
        writer.flush();
        writer.close();
    }

    public static JSONObject createJSON(HashMap<String, HashMap<String, WordFeature>> wordTag) {
        JSONObject features = new JSONObject();
        Iterator<Map.Entry<String, HashMap<String, WordFeature>>> it = wordTag.entrySet().iterator();

        while (it.hasNext()) {
            Map.Entry<String, HashMap<String, WordFeature>> pair = it.next();
            HashMap<String, WordFeature> key = pair.getValue();
            Iterator<Map.Entry<String, WordFeature>> itKey = key.entrySet().iterator();

            String tag = pair.getKey().toLowerCase();
            int i = 1;
            while (itKey.hasNext()) {
                Map.Entry<String, WordFeature> pairKey = itKey.next();
                features.put(tag + i, pairKey.getValue().toJSONObject(tag + i));
                i++;
                itKey.remove();
            }

            it.remove(); // avoids a ConcurrentModificationException
        }

        return features;
    }

    public static void main (String[] args) throws IOException {
        // HoaxAnalyzer.createModel();
        // String command = COMMAND_EXTRACT;
        // String filename = "E:\\GitHub\\hoax-analyzer-ml\\dataset\\idn-hoax\\1.txt";
        String command = args[0];
        String text = args[1];

        switch (command) {
            case COMMAND_PREPROCESS:
                text = Preprocessor.preprocess(text);
                System.out.println(text);
                break;
            case COMMAND_EXTRACT:
                HashMap<String, HashMap<String, WordFeature>> wordTag = FeatureExtractor.extractTag(text);
                System.out.println(createJSON(wordTag).toJSONString());
                break;
            default:
                System.out.println("Unknown command");
        }
    }
}
