import org.json.simple.JSONObject;

/**
 * Created by Tifani on 3/24/2017.
 */
public class WordFeature implements Comparable<WordFeature> {
    public static final String NULL = "null";
    public static final String TOKEN = "token";
    public static final String PROB = "prob";
    public static final String WORD_COUNT = "wcount";
    public static final String WORD_POS = "wpos";
    public static final String SENTENCE_POS = "spos";

    private String token;
    private double prob;
    private int wordCount;
    private int wordPos;
    private int sentencePos;

    public WordFeature(String token, int wordPos, int sentencePos, double n) {
        this.token = token;
        this.wordPos = wordPos;
        this.sentencePos = sentencePos;
        if (token.equals(NULL)) {
            this.prob = 0;
            this.wordCount = 0;
        } else {
            this.prob = n;
            this.wordCount = 1;
        }
    }

    public void incrementCount(double n) {
        this.prob += n;
        this.wordCount++;
    }

    public String getToken() {
        return token;
    }

    public double getProb() {
        return prob;
    }

    public int getWordCount() {
        return wordCount;
    }

    public int getWordPos() {
        return wordPos;
    }

    public int getSentencePos() {
        return sentencePos;
    }

    @Override
    public int compareTo(WordFeature o) {
        if (this.prob == o.prob) {
            if (this.wordPos - o.wordPos > 0){
                return 1;
            } if (this.wordPos - o.wordPos < 0) {
                return -1;
            } else {
                return 0;
            }

        } else {
            if (this.prob - o.prob > 0) {
                return 1;
            } else if (this.prob - o.prob < 0) {
                return -1;
            } else {
                return 0;
            }
        }
    }

    @Override
    public String toString() {
        return token + ": " + prob + " | " + wordCount + " | " + wordPos + " | " + sentencePos;
    }

    public JSONObject toJSONObject(String tag) {
        JSONObject object = new JSONObject();
        object.put(tag + "_" + TOKEN, token);
        object.put(tag + "_" + PROB, prob);
        object.put(tag + "_" + WORD_COUNT, wordCount);
        object.put(tag + "_" + WORD_POS, wordPos);
        object.put(tag + "_" + SENTENCE_POS, sentencePos);

        return object;
    }
}
