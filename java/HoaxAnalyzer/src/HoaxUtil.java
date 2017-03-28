import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;

/**
 * Created by Tifani on 3/24/2017.
 */
public class HoaxUtil {

    public static String loadFile(String path) throws IOException {
        List<String> lines = Files.readAllLines(Paths.get(path));
        return String.join(" ", lines).replaceAll("\\P{InBasic_Latin}", " ").replace("”"," ").replace("”"," ");
    }
}
