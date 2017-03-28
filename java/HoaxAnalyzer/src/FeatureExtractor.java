import IndonesianNLP.IndonesianStemmer;

import java.util.*;

/**
 * Created by Tifani on 3/24/2017.
 */
public class FeatureExtractor {
    private static final int NUM_WORD = 8;
    private static final int NUM_SEN = 2;
    private static final int AVG_WORD = 7;
    public static ArrayList<String> acceptibleTag = new ArrayList<>(Arrays.asList("NNP", "NN", "CDP"));

    public static HashMap<String, HashMap<String, WordFeature>> extractTag(String text) {
        HashMap<String, HashMap<String, WordFeature>> wordTag = new HashMap<>();
        IndonesianStemmer stemmer = new IndonesianStemmer();
        ArrayList<String[]> tags = Preprocessor.tagging(text);

        // Count in Text
        int tokenLength = tags.size();
        int w = 1; // word position
        int s = 1; // sentence position

        for(int i = 0; i < tags.size(); i++) {
            String token = tags.get(i)[0];
            String tag = tags.get(i)[1];
            // System.out.print("(" + tag + "," + token + ") ");

            if (tag.equals("VBI") || tag.equals("VBT")) {
                token = stemmer.stem(token);
                tag = "VB";
            } else if (tag.equals(".")) {
                s++;
            }
            if (acceptibleTag.contains(tag)) {
                token = token.toLowerCase();
                double n = 1 + 2.0 * (tokenLength - w) / (tokenLength * 1.0);
                if (w < NUM_SEN * AVG_WORD) {
                    n += 2;
                }
                try {
                    wordTag.get(tag).get(token).incrementCount(n);
                } catch (Exception ex1) {
                    try {
                        wordTag.get(tag).put(token, new WordFeature(token, w, s, n));
                    } catch (Exception ex2) {
                        wordTag.put(tag, new HashMap<>());
                        wordTag.get(tag).put(token, new WordFeature(token, w, s, n));
                    }
                }
            }
            w++;
        }
        //System.out.println();

        for(String key : acceptibleTag) {
            if (wordTag.containsKey(key)) {
                wordTag.put(key, sortByValue(wordTag.get(key)));
            } else {
                wordTag.put(key, new HashMap<>());
            }
            int j = 1;
            while (wordTag.get(key).size() < NUM_WORD) {
                wordTag.get(key).put(WordFeature.NULL + "_" + j, new WordFeature(WordFeature.NULL, 0, 0, 0));
                j++;
            }
        }
        return wordTag;
    }

    public static void printTag(HashMap<String, HashMap<String, WordFeature>> wordTag) {
        Iterator<Map.Entry<String, HashMap<String, WordFeature>>> it = wordTag.entrySet().iterator();
        while (it.hasNext()) {
            Map.Entry<String, HashMap<String, WordFeature>> pair = it.next();
            HashMap<String, WordFeature> key = pair.getValue();
            Iterator<Map.Entry<String, WordFeature>> itKey = key.entrySet().iterator();

            while (itKey.hasNext()) {
                Map.Entry<String, WordFeature> pairKey = itKey.next();
                System.out.println(pairKey.getValue().toString());
                itKey.remove();
            }
            System.out.println();
            it.remove(); // avoids a ConcurrentModificationException
        }
    }

    private static HashMap<String, WordFeature> sortByValue(HashMap<String, WordFeature> map) {
        List<Map.Entry<String, WordFeature>> list = new LinkedList<>(map.entrySet());
        Collections.sort(list, new Comparator<Object>() {
            @SuppressWarnings("unchecked")
            public int compare(Object o1, Object o2) {
                return (((Map.Entry<String, WordFeature>) (o2)).getValue()).compareTo(((Map.Entry<String, WordFeature>) (o1)).getValue());
            }
        });

        HashMap<String, WordFeature> result = new LinkedHashMap<>();
        int i = 1;
        for (Iterator<Map.Entry<String, WordFeature>> it = list.iterator(); it.hasNext();) {
            Map.Entry<String, WordFeature> entry = it.next();
            result.put(entry.getKey(), entry.getValue());
            if (i < NUM_WORD) {
                i++;
            } else {
                break;
            }
        }

        return result;
    }

}
