# Large multilingual noise-word list for Telegram trend analysis
# Use this file from trend.py:
# from noise_words import NOISE_WORDS

NOISE_WORDS = {
    # ---------------- ENGLISH: COMMON WORDS ----------------
    "a", "an", "the", "and", "or", "but", "if", "then", "than", "so",
    "as", "at", "by", "for", "from", "in", "into", "of", "on", "onto",
    "to", "up", "with", "without", "about", "above", "below", "between",
    "under", "over", "after", "before", "during", "through", "against",
    "among", "around", "near", "off", "out", "per", "via", "within",
    "this", "that", "these", "those", "it", "its", "itself",
    "i", "me", "my", "mine", "myself", "we", "us", "our", "ours",
    "ourselves", "you", "your", "yours", "yourself", "yourselves",
    "he", "him", "his", "himself", "she", "her", "hers", "herself",
    "they", "them", "their", "theirs", "themselves",
    "who", "whom", "whose", "which", "what", "whatever",
    "where", "when", "why", "how",

    # ---------------- ENGLISH: VERBS / AUXILIARY ----------------
    "am", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "having",
    "do", "does", "did", "doing",
    "can", "could", "may", "might", "must", "shall", "should",
    "will", "would", "need", "needs", "needed",
    "want", "wants", "wanted", "get", "gets", "got", "getting",
    "make", "makes", "made", "making",
    "go", "goes", "went", "going",
    "come", "comes", "came", "coming",
    "take", "takes", "took", "taking",
    "give", "gives", "gave", "giving",
    "see", "sees", "saw", "seeing",
    "know", "knows", "knew", "knowing",
    "think", "thinks", "thought", "thinking",
    "say", "says", "said", "saying",
    "tell", "tells", "told", "telling",
    "use", "uses", "used", "using",
    "try", "tries", "tried", "trying",
    "keep", "keeps", "kept", "keeping",
    "let", "lets", "left", "leave", "leaves", "leaving",
    "look", "looks", "looked", "looking",
    "find", "finds", "found", "finding",
    "give", "gave", "given",
    "put", "puts", "putting",
    "show", "shows", "showed", "showing",
    "ask", "asks", "asked", "asking",
    "work", "works", "worked", "working",
    "seem", "seems", "seemed",
    "feel", "feels", "felt",
    "become", "becomes", "became",
    "start", "starts", "started", "starting",
    "stop", "stops", "stopped", "stopping",

    # ---------------- ENGLISH: COMMON CHAT / SOCIAL NOISE ----------------
    "hello", "hey", "hi", "hii", "hiii", "hiiii", "hlo", "helo",
    "hola", "thanks", "thank", "thankyou", "thankyouall",
    "please", "pls", "plz", "welcome", "sorry", "ok", "okay", "okk",
    "okkk", "yes", "yeah", "yep", "yup", "no", "nope",
    "sure", "fine", "good", "great", "nice", "cool", "wow",
    "lol", "lmao", "haha", "hahaha", "hehe", "hehehe",
    "bro", "brother", "sis", "sir", "madam", "guys", "guy",
    "friend", "friends", "everyone", "everybody", "people",
    "admin", "admins", "member", "members", "team", "all",
    "dear", "kindly", "request", "regards",

    # ---------------- ENGLISH: GENERIC / LOW-INFORMATION WORDS ----------------
    "also", "just", "only", "even", "still", "already", "again",
    "very", "really", "quite", "much", "many", "more", "most",
    "less", "least", "some", "any", "each", "every", "both",
    "either", "neither", "another", "other", "others",
    "same", "such", "own", "new", "old", "first", "last",
    "next", "back", "here", "there", "now", "today", "tomorrow",
    "yesterday", "day", "days", "time", "times", "way", "ways",
    "thing", "things", "something", "anything", "nothing",
    "everything", "one", "ones", "two", "three", "four", "five",
    "six", "seven", "eight", "nine", "ten",
    "like", "looks", "look", "right", "left", "well", "maybe",
    "perhaps", "actually", "basically", "probably", "usually",
    "often", "sometimes", "always", "never", "ever", "yet",
    "back", "forward", "away", "together", "enough",

    # ---------------- TELEGRAM / INTERNET BOILERPLATE ----------------
    "telegram", "channel", "channels", "group", "groups",
    "post", "posts", "posting", "posted", "message", "messages",
    "msg", "msgs", "update", "updates", "updated", "latest",
    "news", "information", "info", "details", "link", "links",
    "click", "follow", "following", "subscribe", "subscribed",
    "join", "joined", "share", "shared", "sharing",
    "forward", "forwarded", "download", "file", "files",
    "source", "sources", "read", "watch", "watching",
    "check", "checking", "see", "visit", "visitnow",
    "available", "availability", "official",
    "http", "https", "www", "com", "org", "net",

    # ---------------- HINDI / HINGLISH ROMANIZED ----------------
    "hai", "hain", "ho", "hun", "houn", "tha", "thi", "the",
    "thaa", "thii", "tha", "rah", "raha", "rahi", "rahe",
    "kar", "karo", "kare", "karen", "karta", "karti", "karte",
    "kiya", "kiye", "gaya", "gayi", "gaye", "ja", "jaa",
    "jana", "jane", "jaana", "a", "aa", "aaya", "aayi", "aaye",
    "aur", "or", "ka", "ki", "ke", "ko", "se", "me", "mein",
    "par", "pe", "tak", "liye", "liye", "liye", "ne",
    "ye", "yeh", "yah", "wo", "woh", "vo",
    "is", "iss", "us", "uss", "in", "un",
    "ek", "do", "bhi", "bhe", "to", "toh",
    "kya", "kyu", "kyun", "kyunki", "kaise", "kab", "kahan",
    "kon", "kaun", "kis", "kise", "kiska", "kiski", "kiske",
    "nahi", "nahin", "nhi", "haan", "han", "ha",
    "bas", "sirf", "phir", "fir", "ab", "aaj", "kal",
    "kal", "yaha", "yahaan", "waha", "wahaan",
    "sab", "sabhi", "kuch", "koi", "kisi", "har", "har",
    "bahut", "zyada", "kam", "thoda", "thodi", "thode",
    "acha", "accha", "achha", "achhi", "achhe",
    "sahi", "galat", "mat", "matlab", "lagta", "lagti",
    "wala", "wali", "wale", "waala", "waali", "waale",
    "apna", "apni", "apne", "mera", "meri", "mere",
    "tera", "teri", "tere", "unka", "unki", "unke",
    "hamara", "hamari", "hamare",
    "mujhe", "mujh", "mujhse", "hume", "hum", "ham",
    "aap", "ap", "aapka", "aapki", "aapke",
    "tum", "tumhe", "tumhara", "tumhari", "tumhare",
    "woh", "uska", "uski", "uske",

    # ---------------- HINDI / HINGLISH CHAT SLANG ----------------
    "bhai", "bhaai", "bro", "yaar", "yar", "dost", "dosto",
    "sir", "mam", "maam", "ji", "jii",
    "lol", "haha", "hehe", "hahaha",
    "kr", "krna", "krne", "krta", "krti", "krte",
    "karo", "karna", "karne", "karna", "karta", "karti",
    "bta", "btana", "bata", "batana", "batao",
    "de", "do", "dena", "dene", "diya", "di",
    "le", "lo", "lena", "lene", "liya", "li",
    "rha", "rhi", "rhe", "raha", "rahi", "rahe",
    "gya", "gyi", "gye", "gaya", "gayi", "gaye",

    # ---------------- COMMON URDU / ROMAN URDU ----------------
    "hai", "hain", "tha", "thi", "the", "aur", "ya",
    "ye", "woh", "is", "us", "ko", "ka", "ki", "ke",
    "se", "mein", "me", "par", "pe", "tak",
    "kya", "kyun", "kaise", "kab", "kahan", "kaun",
    "nahi", "nahin", "haan", "ji", "bas", "sirf",
    "sab", "kuch", "koi", "har", "bhi",
    "bohat", "bahut", "zyada", "kam",

    # ---------------- COMMON EMOJIS / TEXT TOKENS ----------------
    "emoji", "emojis", "rt", "amp", "via",
    "nbsp", "quot", "apos", "undefined", "null", "none",
    "nan", "true", "false",

    # ---------------- GENERIC NUMERIC / DATE TOKENS ----------------
    "2020", "2021", "2022", "2023", "2024", "2025", "2026",
    "2027", "2028", "2029", "2030",
}

# Add common noisy URL / file / platform fragments programmatically.
NOISE_WORDS.update({
    "t", "co", "bit", "ly", "tinyurl", "youtu", "youtube",
    "instagram", "facebook", "twitter", "xcom", "tme",
    "pdf", "jpg", "jpeg", "png", "gif", "mp4", "mp3",
})

# Normalize everything once so trend.py can compare lowercase tokens.
NOISE_WORDS = {str(x).lower().strip() for x in NOISE_WORDS if str(x).strip()}
