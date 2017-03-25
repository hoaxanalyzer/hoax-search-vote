import logging
import json

from analyzer import Analyzer
from article import Article

# for query in queries:
# 	analyzer = Analyzer(query)
# 	result = analyzer.do()
# 	print(result["scores"])
# 	print(result["conclusion"])

# content = "News of actress Sherri Shepherds death spread quickly earlier this week causing concern among fans across the world. However the March 2017 report has now been confirmed as a complete hoax and just the latest in a string of fake celebrity death reports. Thankfully, the host of The View is alive and well. UPDATE 09/03/2017 : This story seems to be false. (read more) Rumors of the actresss alleged demise gained traction on Tuesday after a R.I.P. Sherri Shepherd Facebook page attracted nearly one million of likes. Those who read the About page were given a believable account of the American actresss passing: Hundreds of fans immediately started writing their messages of condolence on the Facebook page, expressing their sadness that the talented 49-year-old actress, comedienne and television host was dead. And as usual, Twittersphere was frenzied over the death hoax. Where as some trusting fans believed the post, others were immediately skeptical of the report, perhaps learning their lesson from the huge amount of fake death reports emerging about celebrities over recent months. Some pointed out that the news had not been carried on any major American network, indicating that it was a fake report, as the death of an actress of Sherri Shepherd's stature would be major news across networks. A recent poll conducted for the Celebrity Post shows that a large majority (91%) of respondents think those Sherri Shepherd death rumors are not funny anymore. Sherri Shepherd Death Hoax Dismissed Since Actress Is Alive And Well On Wednesday (March 08) the actress' reps officially confirmed that Sherri Shepherd is not dead. She joins the long list of celebrities who have been victimized by this hoax. She's still alive and well, stop believing what you see on the Internet, they said. Some fans have expressed anger at the fake report saying it was reckless, distressing and hurtful to fans of the much loved actress. Others say this shows her extreme popularity across the globe. 2017 MediaMass All rights reserved. Do not reproduce (even with permission)."
# article = Article("sherry shepperd die", "1.txt", "test.com", content, "None")

# print(article.feature_fact)
# print("====== ====== ====== =====")
# print(article.feature_hoax)
# print("====== ====== ====== =====")
# print("====== ====== ====== =====")
# print(article.ofeature_fact)
# print("====== ====== ====== =====")
# print(article.ofeature_hoax)

trainqueries = [["Skype and Twitter are all banned in China.", "005d445fa9e87175d8b3ed8d6dbca5be401f368b2fefae9bb31a4a45dd669798"],
["Hillary Clinton once lauded the Trans-Pacific Partnership (which she later opposed) as setting the gold standard in trade agreements.", "02de749f780592f581ac0d1dc2bedbd42ee0b170cce6f5535d1d99c14499a15c"],
["The state of Wisconsin banned all FoodShare/EBT programs through 2019 due to budgetary concerns", "0455eca4c35e38d5421ffa41eee3bb8c121757afc8aec23fd178faffcafc7bc7"],
["A lion's roar can be heard from 5 miles away!", "045972b7662731daba8bad2299c10cb4db8cbec10336df10d66481455261c2b3"],
["Cherophobia is the fear of fun", "058d9d44035fb3718dd79e432d269af407ed1f35e603baf10aebab7883b68413"],
["Australia is the first country to begin microchipping its citizens.", "0769760f5892d6b7a1bcd4149a246c94f10d7dc5a8b6c764cc43b6c79de75d78"],
["Sherry Shepperd Die", "08340407fb0db6624b6f8188d20ae3b37ab4f8b9973dcd15b387f18a2ef66a57"],
["Free Cone Day from Daily Queen Holding", "08e63fb9449dfc3803f3fbd65b5885ab87d15444072051bdc0b2a73e05bae86d"],
["Media giant Time Warner declined to renew CNN's contract.", "099df2e88dee01c475bbd6ec091ddabd5c61c1a21c247fe43e7141454a6855b1"],
["Tommy Chong Death", "0a94d3ebc06e7fb97a3bdcb8dc8c062e88c6c6a51d7abf65953f3a21d8e0971b"],
["Ivana Trump claimed her famous ex-husband Donald is addicted to penile enhancement pills.", "0abcbf558e0ed527033c80c9473b3f070741718e63a3a378955fff9a40eecb7f"],
["Charles Manson Death", "0c0725c7a5e164efe3f84a619d1b20e71823c4719e0e07fcd4f9b17cec0bfcb2"],
["Indonesia is largest archipelago", "0c25fa889de0724e1c1ac99f7206af75da46d00868784cbef0f98fb41bf29179"],
["Nutella Burger Mc'Donalds", "0dbca87703c0eb5141bf15c79fa7f168ea76ba8ff19dd897dc4c5d7c79faf6a8"],
["Leonardo DiCaprio endorsed Republican presidential nominee Donald Trump on Twitter.", "0f1961c6901972c50465ba2ce24e5ab891673f44b67cb6f3e34d3008b6cbbf9d"],
["Indonesia largest moslem population", "0f2a73e52abe0c0a4c7b96cdd34e894078d18fd051f1b24e3310114cd94c3f89"],
["Baseball's championship competition is known as the World Series because it was originally sponsored by the newspaper.", "132e965bbd6ca0d90a7a759ec22c4764e9e3ad9b8e908993f7214fb12aa26bdf"],
["Big Show was killed in a car accident", "13ede3feb3a48a5cc23d5a068ffe80b5c0124f40fbf3688ef7f8329881c707c3"],
["NBC's long-running 'Saturday Night Live' has been cancelled due to low ratings.", "14ab2d03f02765c0aed051e4d1338a3fae563579378deae7135f598bca0c0316"],
["Betty White Death", "19c1b3fdea241c7c7331d916912624baf8a638834898ca799c0a9e146e560944"],
["Barack and Michelle Obama have filed for divorce in Illinois.", "1a0f1694cb65044a84a6219fbaf4dd39f0f48da0087a02ccce65cba993222d4b"],
["Rowan Atkinson Death", "1cccaab80b174d8fd6ad0558fd30067edbd664d37b5d451bb4f520bdc34888af"],
["House speaker Paul Ryan asserted that women who use birth control are committing murder.", "1f9b17a5a401d6b62c03ba452de7393d51ea266b47e134d2e7abfb0b533aebad"],
["Hillary Clinton wore a secret earpiece during the first presidential debate of 2016.", "1ff162741a34aca067ccfc5d0355c0903ab5f02b665449db2bc6f291cf2bc00b"],
["Stevie Wonder was killed in a car crash", "2062bb52acc4a5742ea2d342a8b2506c7049b68409041ed3fdbcd755da77b6ab"],
["Jokowi is the Indonesia president", "225a269ec42e269fdc93f58b8a33107413c14c2bd4e0f0e5b1cb5172ca1d5bfc"],
["A napping morgue worker in Texas was accidentally cremated by a coworker.", "231df86f40662b4098af6e5b539fc34d0fe60111bf116b7a895b450473cb68bb"],
["Suharto was the most corrupt leader of all time", "2325c036791829c1c1fc1b73dd87eef823784a1b536568079dfec68904490b79"],
["When hippos are upset", "26826b83fcd949a64704549e4b0a12e9f0ee78a9c15ec99eff157663c75a976a"],
["Betsy Devos say history textbook should be based on bible", "291aade3c15dbd0d6401c0ec426d8ad4aea858487330518097f0135c15cd33ce"],
["Ruth Bader Ginsburg has resigned her U.S. Supreme Court seat and moved to New Zealand.", "29377ecddf1b2c7fd2d612150a61c34a7be556f1d7332772104ffb8417845c16"],
["After breaking up with Brad Pitt Angelina Jolie decided to return her adopted children to orphanages in order to focus on her career.", "2b9b30abeeaca977ad613455c9ab4de49235a536c561d3b736d85079ace7ff89"],
["Japanese citizens is illegal to overweight", "2f5b5902d632ec6743ab234822719bfc63581a39ea5c9bb4999e61537175c049"],
["The Fraternal Order of Police have retracted their endorsement of Donald Trump.", "30e469f60f65fb974bffe88eafebd14d18434a9834e3ef8dcbfb630132ecb986"],
["A video shows a shopper being struck by an inflatable raft inside a department store.", "3126568cc116bb1b29994e61ea7b435e83ae3e67828c7b82ac252b59558e0b9f"],
["Indonesia and Monaco have the same flag", "314c6a1e50d663b51fab6abb4b12e55a0046263c8f43547085cea12104ec8e61"],
["A photograph shows Donald Trump posing with his parents in Ku Klux Klan robes.", "316eeebfe69cc0f11105a2057ecf74effa5e62c19bf3de799dcbc58d10aed8c4"],
["Donald Trump was born in the Philippines and not Queens New York as he claims.", "326c1dc3d0cfd09759de03ec368c6fc5d8f40a309c6109d2852738a88653511f"],
["Harambe received 15", "3672bb6bd1719b5ea441940c4ca41832a52d28d9718953627de74d4da3a804f0"],
["The Ford Motor Company donated $100 million to the Black Lives Matter movement.", "36fba891aa4dbf51c4a48d9eac25308bf71e9a17e074830525fcc72db89f785e"],
["An African Union Travel Advisory warned Africans heading for the U.S. about continued instability in America.", "37aef1aff6d685d0d62d8b536a2b26fbecfae346a666f5e68559dd667cbe63e2"],
["A photograph show Ivanka Trump with Vladimir Putin and Wendi Murdoch.", "3901c92e30644e4326a85f62a6d13dd4123911bb09a25f5cb94e3430f943eced"],
["Montreal's city council ban pit bulls", "3a7e40b988f0db8656f41eafcfd67d028cb6dac5264a8a82fb820fb37ae36142"],
["Reggae musician Buju Banton killed himself in prison.", "3f6b5ef30ea1719ce2adc6bf06a483c0b9b9c671c4dac238e102bf8c271943e1"],
["Thousands of pre-marked ballots for Hillary Clinton and other Democratic candidates were found in a warehouse in Ohio.", "46308321b499cf360f2521cbcb208685fb65b845e7112fdc2d2fe6af5b84a00b"],
["Younger brother kill big brother pokemon go", "47ffa7cc99977c04f3da47d4d8dc0de5d952fe01191e4dac683eddac559f93c9"],
["A baby octopus is about the size of a flea when it is born", "480c77e2246c35225f7f0b44440ab92eb65c7c97f91cba87563dc39c042cc066"],
["Elvis Presley got a 'C' in his 8th grade music class", "4b42a2376ef30904a8a7f25da5d3ea89b8b416a747ae1df946d1a0209d43d654"],
["clocks Pulp Fiction 4:20", "4ce175becd4bae60ac03e02a55fdf30b0df6b902880371ebf93809f3fabb5aaf"],
["A man died in a meth lab explosion after attempting to light his own flatulence.", "514532357cd38960b5ec82cfdf2702c2ad4d127b74552c95b4afcde473cedea3"],
["Reginald VelJohnson Death", "51f16892c405fa9cf591e63934f328689855bf21555f91f29549e8b83640f06b"],
["A woman saved multiple lives by using her concealed carry pistol to take down a department store shooter in Virginia.", "54ac87fd9b40dadbeb012357715349210f66d054a5d4c225e95bcb6efb63e1d5"],
["Preacher Joel Osteen was horrified at recently learning that Jesus was crucified.", "58597b17e196e01e2fb1636cbcb3d4f8799ff415dc995b6c923495d8edfe3c5d"],
["Soekarno is the first president of Indonesia", "5b09d5700fa64044a482f960514d358402a3c4b9b68f7cb9ad5e18a8b4283e74"],
["A special property of the equinox allows eggs (or brooms) to be balanced on their ends that day.", "5c4a401a83e255b7316ebaa2e5d9f846845cc724b76fc5a5d67b2d35fb224dd5"],
["Mark Zuckerberg will delete Donald Trump's or Hillary Clinton's Facebook pages for 500,000 likes. ", "5d66926bdc9fbc01541f969327cc25e69e6217bdb10c29b8d8f8dbd5283ed1fd"],
["Actor Bill Murray said in order to teach children about taxes, eat their ice cream.", "65e6a39103a9e360e8c43255e07692a0a9e4ff1a6456f35ffc6c64a59234c13a"],
["Bananas are curved because they grow towards the sun.", "6620609201243218b7b64868cd38cacdc1be9655fa10554565778bde2c376473"],
["Jokowi is christian", "66387e8b91fad9fd9751632df7d720ebb2644d76a5c8544c9d333c6cf1dd3c35"],
["George Soros Dies of Heart Attack", "6a16d36c7478f930a73dcbe965d67eacd719e20c50ed6d9c0b8891b1888b0db3"],
["Michael Bloomberg said that Donald Trump was known among millionaires as a 'con artist, ' and among business owners as a 'cheat.'", "6b4dfe0bb0d6f99321a2006242c5e1365e8c0986c87269b34e4c897042c4ba4b"],
["The animated TV show 'SpongeBob SquarePants' has been canceled.", "7039c9016dec0fa7a6ae83e283299a14202349eccd62d7463a6f81b9727407e1"],
["Hillary Clinton and moderator Lester Holt rigged the first presidential debate by communicating via secret hand signals.", "72ec08f85c10026c82b8ccf4c61df421c20f204a64de736d38b8085b531144e8"],
["Hillary Clinton and John Kerry were nominated for a Nobel Peace Prize for negotiating a nuclear deal with Iran.", "7422e00db36ddb332244a669b167f3f9889d1aedb4cb0f6b10a5dcf8b4a00051"],
["A video shows a woman stabbing her baby to death to gain revenge on her boyfriend.", "7430c3d3b46ca76c4dc61ca5d58074bd0b763aecef58ff97950d7692f532fb88"],
["A man saw dead people and talked to God after he was deprived of his senses during a government experiment.", "794fe8f77cedefd2077d3d8c7bf8a94ef290b24622411171214d09cb0792538a"],
["Jokowi is chinese", "799a9082392ec0bde6ffb1ff8e6e756fdd9fbfbee2d54c5b73629318e5894b47"],
["President Trump has signed a bill lowering the age of sexual consent to 13.", "7bace9490ce9923ccd476e829541bcf0f66d19676fca0c3554b02973ff0183da"],
["Nicolas Cage Death", "7bf15f955304f59dc74f828bb0089fe109364cb530a8845fddab63363df5f7e2"],
["King Salman visit Bali", "7fc876724ea4f034fc1bd144027e159e942726dfbb13cb849bd92464f4786ffd"],
["70 per cent of the persons arrested during protests in Charlotte had out-of-state IDs.", "86cde7001b028a694d39ab97010bfc72b5652303fcb2439a5e39f8cefa765f52"],
["Forbes 2011 McDuck $44 billion", "89e1ca24ad7a95536f8e23f54fa7348b54c17607487f8e2698a825587ac701f6"],
["Brad Pitt Death", "92ae0a0319e63936ade4eba7c605a6fafe45befb69ef0de339c0247b8a1307cf"],
["Airport scanners rip apart DNA", "9412b5e80c142d04cb9f919be8681e0fce8a66967d4d60b2538ff150b4983cd1"],
["Eric Braverman", "a40758870e158e0583ceb93d083d6371e314a9cb544979ba613a05c67b8b07ac"],
["Egplant-flavored condom durex", "ad527f584b829d0bd7ad58825180f063bbebd160800b1f9396754b0b9383b380"],
["Nelson Mandela Death", "b1976fa56518df560089bf03156d37495d53253a23c22d77c39ae39bd2f491df"],
["President Obama took a knee during the national anthem.", "b3ac7ab2322e8640163296226c80e020f560d8eaf2187e7ee34e10cae201c27f"],
["A man wearing a clown costume was shot in Fort Wayne, Indiana.", "b655b06af08037049f219c118288a0f492769ad9f839cfb9cbe7d4d22dc6c988"],
["Miss Universe Alicia Machado Porn Star", "bbdfd5f847b10f8756c073592afba66049fddd34e7b1b15c9496e7918a453c4c"],
["Joyce Meyer Died 73 October 2016", "bc871ef720f4b624d0f09c435c2b3b287a218f24b1e2e8f364930578d9f3765a"],
["Jellyfish 95 percent water", "bcff06143c1ff8d015b9a5c62275cbbf48116eaf9e486b2d535f69d9184d653c"],
["Paracetamol contaminated with a dangerous virus", "c0e3910c7156bdfba7e925b70d8df03283b1ef021c7427899e179e090ca48add"],
["Borobudur temple in Central Java", "c620f8c89d92e66c40558848b8b7c6bf1dbe5da0be2ffe8bbf8af08fa05d924f"],
["Left Handed People Die Younger Than Right Handed People", "ca39e3bfe2ea322c250266be1ec6ec5eaa853c702dd73b1e1fc76cadd95bfad0"],
["Japanese invaded and occupied Indonesia 1942", "ce219bc50a38866780d4869393c14559ffa41cbb3664a331fcb4f70de5c9940c"],
["George Bush Death", "d1d554d4ba731a619e224ec4ddba65d63b542403e990d9c916150522e3dcc7f3"],
["John Cena Death", "d3fe1d73e9f7f248db1613988adabbe2df44b08162b95106180dfe678522eebb"],
["Donald Trump has called global warming a hoax on multiple occasions.", "d4a4aa97a314a586648c8a68081561cea20f7dbe7dfa940ee0cf388b3ac636e1"],
["The Komodo dragon is the largest lizard in the world", "dc6d9cd7fa62f5bab966800d37dd42a3b63637217824755c47e50fbe85ab5451"],
["Eat mince pies on Christmas Day in UK illegal", "e013b2f26f48214b669bcc1a30acc7d5f32b24035766cd980b2a06c092c2faa8"],
["Canadian prime minister Justin Trudeau announced a new law to arrest and fine anyone wearing clown costumes.", "e9c0b0a4fd7bc2435773c971ae400cf2ecbb24ff8285715ed9ebc63b22e637a6"],
["Zsa Zsa Gabor Dies in 99", "ec4268f0b0c534cef835f7421b8340dc9157de244c996401304358464001808a"],
["Evolution fresh drinks poison", "ef04e13aea0ae5a45b4389c19a7bc24da95fe5f92b9c7328fa543a745a575230"],
["KFC create a chickhen-scented candle", "f2dc19367ea5fefaaeb0f87929f88836173045c5bf71faf049ab3306ea47ede2"],
["Hillary Clinton received her questions for the first presidential debate of 2016 a week in advance.", "f93fd25f63a1541c15eae4e36b31ca668b612a2c50c04dd07e8d0092c85f6eb7"],
["A photograph shows Barack Obama sitting with Malcolm X and Martin Luther King, Jr.", "f9d2eeb2d41e254fb568d0de31713e603161deacc0529b784a741dd89f932ed5"],
["Giant squid found in New Zealand", "fa7a4633274f7f12398dc5f515980c04534ca9dbbb91f38196d8c859ba8a52e2"],
["Over-the-counter painkiller paracetamol is contaminated with the Machupo virus and should be avoided.", "fb2b7440161d0c213f2d4974fdeb4868660ea84d605ee3e76aafc160c2a888d7"],
["A video shows Black Lives Matter protesters in Charlotte attacking and beating a homeless vet.", "fb74317510048c7bcd071ad32e70625c4f680ce2a7124ce544647d32959541bf"],
["U.S. President George Washington had wooden teeth.", "ff076c0f665e4303bfd8c2eb670f2fd6788c3122ee38d4e9461b53c8183c23ce"],
["Weapons-wielding clowns from the U.S. invaded Canada and murdered 23 victims.", "ff8d9d0afff3f1b09aa869bb18c509619e7350bc51c40a76496820756bf84003"]]

testqueries = ["Free Cone Day from Daily Queen Holding",
"Left Handed People Die Younger Than Right Handed People",
"Betsy Devos say history textbook should be based on bible",
"Paracetamol contaminated with a dangerous virus",
"Tommy Chong Death",
"Jokowi is chinese",
"Jokowi is christian",
"Airport scanners rip apart DNA",
"Reginald VelJohnson Death",
"Jokowi is the Indonesia president",
"King Salman visit Bali",
"Eat mince pies on Christmas Day in UK illegal",
"Cherophobia is the fear of fun",
"When hippos are upset, their sweat turns red",
"Bananas are curved because they grow towards the sun.",
"A lion's roar can be heard from 5 miles away!",
"Facebook, Skype and Twitter are all banned in China.",
"A baby octopus is about the size of a flea when it is born",
"Japanese invaded and occupied Indonesia 1942",
"Soekarno is the first president of Indonesia",
"George Bush Death",
"Japanese citizens is illegal to overweight",
"The Komodo dragon is the largest lizard in the world",
"Suharto was the most corrupt leader of all time",
"Indonesia largest moslem population",
"Indonesia is largest archipelago",
"Borobudur temple in Central Java",
"Indonesia and Monaco have the same flag",
"Evolution fresh drinks poison",
"Sherry Shepperd Die",
"Charles Manson Death",
"Eric Braverman",
"Stevie Wonder was killed in a car crash",
"Big Show was killed in a car accident",
"Zsa Zsa Gabor Dies in 99",
"Nutella Burger Mc'Donalds",
"KFC create a chickhen-scented candle",
"Giant squid found in New Zealand",
"George Soros Dies of Heart Attack",
"Harambe received 15,000 votes in the 2016 US Election",
"clocks Pulp Fiction 4:20",
"Forbes 2011 McDuck $44 billion",
"Nelson Mandela Death",
"Betty White Death",
"Joyce Meyer Died 73 October 2016",
"Montreal's city council ban pit bulls",
"Miss Universe Alicia Machado Porn Star",
"Brad Pitt Death",
"Jellyfish 95 percent water",
"Egplant-flavored condom durex",
"Elvis Presley got a 'C' in his 8th grade music class",
"Rowan Atkinson Death",
"Younger brother kill big brother pokemon go",
"Nicolas Cage Death",
"John Cena Death",
"Richard Harrison Death",
"Author Cormac McCarthy passed away in June 2016",
"Free concert tickets ticketmaster",
"Actor Ralph Macchio of 'Karate Kid' fame passed away in June 2016",
"Actor Jack Black passed away in June 2016",
"WhatsApp Gold premium service",
"Yosemite Sam banned by television",
"Matthew Mccogney is Interstellar actor",
"King Jong Nam killed in Malaysia",
"Marvel Comics writer Stan Lee passed away in May 2016",
"Americans are immune to the Zika virus",
"Mark Zuckerberg Harvard dropped out",
"Steve Jobs Death",
"iphone 7 with no jack",
"Google HTC made pixel phone",
"Obama is the first dark skinned American President",
"Wayne Rooney play for Manchester United",
"Lionel Messi got ballon the or",
"Habibie wife is Ainun",
"Tokodai University in Japan",
"HK UST in Hongkong",
"Actor Anthony Hopkins has died"]

# for query in testqueries:
# 	analyzer = Analyzer("", query)
# 	result = analyzer.do()
# 	print result["conclusion"]
	#print result["scores"]


### TEST ONLY ONE QUERY with SPECIFIC HASH ###
specific = ["Weapons-wielding clowns from the U.S. invaded Canada and murdered 23 victim", "ff8d9d0afff3f1b09aa869bb18c509619e7350bc51c40a76496820756bf84003"]
#analyzer = Analyzer("", "anjing is flat", None, "97a3c518048f46be982973635c3c78ec")
# analyzer = Analyzer("", "earth is flat")
# result = analyzer.do()
# print result["conclusion"]

analyzer = Analyzer("", specific[0])
result = analyzer.do()
print(result["scores"])
print(result["conclusion"])
# http://stackoverflow.com/questions/38076220/python-mysqldb-connection-in-a-class

### DATASET CREATOR ###
# for query in trainqueries:
# 	analyzer = Analyzer("", query[0], None, query[1])
# 	result = analyzer.generate_dataset()