<?php
  // proksi arg curl: --proxy http://167.205.22.102:8080

function extractString($string, $start, $end) {
    $string = " ".$string;
    $ini = strpos($string, $start);
    if ($ini == 0) return "";
    $ini += strlen($start);
    $len = strpos($string, $end, $ini) - $ini;
    return substr($string, $ini, $len);
}

function strip_tags_content($text) {

    return preg_replace('@<(\w+)\b.*?>.*?</\1>@si', '', $text);

 }

  for ($page = $argv[1]; $page <= $argv[2]; $page++) {
    fwrite(STDERR, "NOW PAGES ".$page."\n");
    $url = "curl -L http://www.snopes.com/category/facts";
    if ($page != 1) {
      $url = $url."/page/".$page;
    }
/*
    $url = $url." -H \"Host: www.snopes.com\" \
    -H \"User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0\" \
    -H \"Accept: text/html,application/xhtml+xml,application/xml;q=0.9\" \
    -H \"Accept-Language: en-US,en;q=0.5\" \
    -H \"Accept-Encoding: gzip, deflate\" \
    -H \"Cookie: bme=1; advanced_ads_browser_width=1291\" \
    -H \"DNT: 1\" \
    -H \"Connection: keep-alive\" \
    -H \"Upgrade-Insecure-Requests: 1\" \
    -H \"If-Modified-Since: Fri, 10 Mar 2017 06:42:56 GMT\" \
    -H \"If-None-Match: 0e39c4d718bac78dc55b71fe7207cd2f\" \
    -H \"Cache-Control: max-age=0\"";
*/
    fwrite(STDERR, $url."\n");

    $ret = shell_exec($url);
    $url_pattern = "!http?://\S+!";

    preg_match_all($url_pattern,$ret,$a);

    $count = count($a[0]);
    fwrite(STDERR, "Number of Urls = " .$count."\n");

    $links = [];
    for ($row = 0; $row < $count ; $row++) {
      $str = $a[0]["$row"];
      $pos = strpos($str, "\"");
      if ($pos) {
        $str = substr($str, 0, $pos);
      }

      $ok = false;
      for ($i = 0; $i < strlen($str); $i++) {
        if ($str[$i] == '-') {
          $ok = true;
        }
      }
      if (strpos($str, ".asp")) {
        $ok = true;
      }
      if (strpos($str, "itemprop")
      || strpos($str, "target=\"_blank\"")
      || strpos($str, "www.snopes.com/contact/")
      || strpos($str, "www.snopes.com/category/facts/")
      || strpos($str, "www.snopes.com/whats-new/")
      || strpos($str, "www.snopes.com/50-hottest-urban-legends/")
      || strpos($str, "www.snopes.com/about-snopes/")
      || strpos($str, "www.snopes.com/frequently-asked-questions/")
      || strpos($str, "static.snopes.com")
      || strpos($str, "www.snopes.com/tag/")
      || strpos($str, "www.snopes.com/snopes-staff/")
      || strpos($str, "www.reddit.com/")
      || strpos($str, "www.facebook.com/")
      || strpos($str, "twitter.com")
      || strpos($str, "%20")
      || strpos($str, "www.snopes.com/wp-json/")) {
        $ok = false;
      }

      $pos = strpos($str, "http");
      //echo "lala ".$pos."\n";
      if (strpos($str, "http") !== 0
      || strpos($str, "www.snopes.com") <= 0) {
        $ok = false;
      }

      if ($ok) {
        array_push($links, $str);
      }
    }
    $links = array_values(array_unique($links));


    fwrite(STDERR, "Valid url = ".sizeof($links)."\n");
    for ($i = 0; $i < sizeof($links); $i++) {
      fwrite(STDERR, $links[$i]."\n");

      $buffer = shell_exec("curl -L ".$links[$i]);
      $claim = extractString($buffer, "<p itemprop=\"claimReviewed\">", "</p>");
      $rating = trim(extractString($buffer, "<span itemProp=\"alternateName\">", "</span>"));

      $claim = trim(strip_tags_content($claim));
      $claim = str_replace("\"", "\"\"", $claim);

      if ($claim && $rating) {
        echo "\"".$claim."\";".$rating."\n";
        fwrite(STDERR, "\"".$claim."\";".$rating."\n");
      }
    }
  }
?>
