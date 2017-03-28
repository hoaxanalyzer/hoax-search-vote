import java.io.FileWriter;
import java.io.IOException;
import java.io.Writer;
import java.util.*;

/**
 * Created by Tifani on 3/25/2017.
 */
public class CSVUtil {
    private static final char DEFAULT_SEPARATOR = ',';

    public static void writeLine(Writer w, List<String> values) throws IOException {
        writeLine(w, values, DEFAULT_SEPARATOR, ' ');
    }

    public static void writeLine(Writer w, List<String> values, char separators) throws IOException {
        writeLine(w, values, separators, ' ');
    }

    //https://tools.ietf.org/html/rfc4180
    private static String followCVSformat(String value) {
        String result = value;
        if (result.contains("\"")) {
            result = result.replace("\"", "\"\"");
        }
        return result;
    }

    public static void writeLine(Writer w, List<String> values, char separators, char customQuote) throws IOException {
        boolean first = true;

        //default customQuote is empty
        if (separators == ' ') {
            separators = DEFAULT_SEPARATOR;
        }

        StringBuilder sb = new StringBuilder();
        for (String value : values) {
            if (!first) {
                sb.append(separators);
            }
            if (customQuote == ' ') {
                sb.append(followCVSformat(value));
            } else {
                sb.append(customQuote).append(followCVSformat(value)).append(customQuote);
            }

            first = false;
        }
        sb.append("\n");
        w.append(sb.toString());
    }

    public static void writeToCSV(FileWriter w, String filename, String text, HashMap<String, HashMap<String, WordFeature>> wordTag) throws IOException {
        ArrayList<String> line = new ArrayList<>();
        line.add(filename);
        line.add(text);

        for(int i = 0; i < FeatureExtractor.acceptibleTag.size(); i++) {
            HashMap<String, WordFeature> key = wordTag.get(FeatureExtractor.acceptibleTag.get(i));
            Iterator<Map.Entry<String, WordFeature>> itKey = key.entrySet().iterator();
            while (itKey.hasNext()) {
                Map.Entry<String, WordFeature> pairKey = itKey.next();
                WordFeature wordFeature = pairKey.getValue();
                line.add(wordFeature.getToken());
                line.add(String.valueOf(wordFeature.getProb()));
                line.add(String.valueOf(wordFeature.getWordCount()));
                line.add(String.valueOf(wordFeature.getWordPos()));
                line.add(String.valueOf(wordFeature.getSentencePos()));
                itKey.remove();
            }
            line.add(" ");
        }
        writeLine(w, line, ',', '"');
    }

}
