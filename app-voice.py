from io import BytesIO
import re
import time
from openai import OpenAI
import os
import streamlit as st
from dotenv import load_dotenv
import json
from pydantic import BaseModel, validator, Extra
from typing import List, Optional
import requests
from st_audiorec import st_audiorec
 
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
 
# Make sure you have the API key in the environment variable; otherwise, this will be None.
if openai_api_key is None:
    raise ValueError("OPENAI_API_KEY environment variable not found.")
 
# Set the API key for the OpenAI client
OpenAI.api_key = openai_api_key
 
# openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def load_languages(path_to_languages):
    with open(path_to_languages, "r") as file:
        return set(json.load(file))


languages_en = [
    "aari", 
    "abanyom", 
    "abaza", 
    "abkhaz", 
    "abujmaria", 
    "acehnese", 
    "adamorobe sign language", 
    "adele", 
    "adyghe", 
    "afar", 
    "afrikaans", 
    "afro-seminole creole", 
    "aimaq", 
    "aini", 
    "ainu", 
    "akan", 
    "akawaio", 
    "aklanon", 
    "albanian", 
    "aleut", 
    "algonquin", 
    "alsatian", 
    "altay", 
    "alutor", 
    "american sign language", 
    "amharic", 
    "anda", 
    "amdang", 
    "ancient meitei", 
    "angika", 
    "anyin", 
    "ao", 
    "a-pucikwar", 
    "arabic", 
    "aragonese", 
    "aramaic", 
    "are", 
    "'are'are", 
    "argobba", 
    "aromanian", 
    "armenian", 
    "arvanitic", 
    "ashkun", 
    "asi", 
    "assamese", 
    "assyrian neo-aramaic", 
    "asturian", 
    "ateso", 
    "a'tong", 
    "'auhelawa", 
    "auslan", 
    "austro-bavarian", 
    "avar", 
    "avestan", 
    "awadhi", 
    "aymara", 
    "azerbaijani", 
    "badaga", 
    "badeshi", 
    "bahnar", 
    "balinese", 
    "balochi", 
    "balti", 
    "bambara", 
    "banjar", 
    "banyumasan", 
    "bartangi", 
    "basaa", 
    "bashkardi", 
    "bashkir", 
    "basque", 
    "batak karo", 
    "batak toba", 
    "bats", 
    "beja", 
    "belarusian", 
    "belhare", 
    "berta", 
    "bemba", 
    "bengali", 
    "bezhta", 
    "betawi", 
    "bete", 
    "bhili", 
    "bhojpuri", 
    "bijil neo-aramaic", 
    "bikol", 
    "bikya", 
    "bissa", 
    "blackfoot", 
    "boholano", 
    "bohtan neo-aramaic", 
    "bonan", 
    "bororo", 
    "bodo", 
    "bosnian", 
    "brahui", 
    "breton", 
    "british sign language", 
    "bua", 
    "buginese", 
    "bukusu", 
    "bulgarian", 
    "bunjevac", 
    "burmese", 
    "burushaski", 
    "buryat", 
    "caddo", 
    "cahuilla", 
    "caluyanon", 
    "cantonese", 
    "catalan", 
    "cayuga", 
    "cebuano", 
    "chabacano", 
    "chaga", 
    "chakma", 
    "chaldean neo-aramaic", 
    "chamorro", 
    "chaouia", 
    "chechen", 
    "chenchu", 
    "chenoua", 
    "cherokee", 
    "cheyenne", 
    "chhattisgarhi", 
    "chickasaw", 
    "chintang", 
    "chilcotin", 
    "chinese", 
    "chiricahua", 
    "chichewa", 
    "chipewyan", 
    "chittagonian", 
    "choctaw", 
    "chorasmian", 
    "chukchi", 
    "chulym", 
    "church slavonic", 
    "chuukese", 
    "chuvash", 
    "cocoma", 
    "cocopa", 
    "coeur d\u2019alene", 
    "comanche", 
    "comorian", 
    "cornish", 
    "corsican", 
    "cree", 
    "crimean tatar", 
    "croatian", 
    "cuyonon", 
    "czech", 
    "dagbani", 
    "dahlik", 
    "dalecarlian", 
    "dameli", 
    "danish", 
    "dargin", 
    "dakota", 
    "dari", 
    "dari-persian", 
    "daur", 
    "dena'ina", 
    "dhatki", 
    "dhivehi", 
    "dida", 
    "dioula", 
    "dogri", 
    "dogrib", 
    "dolgan", 
    "domaaki", 
    "dongxiang", 
    "duala", 
    "dungan", 
    "dutch", 
    "dzhidi", 
    "dzongkha", 
    "eastern yugur", 
    "edo", 
    "efik", 
    "esan", 
    "egyptian arabic", 
    "ekoti", 
    "enets", 
    "english", 
    "erzya", 
    "esperanto", 
    "estonian", 
    "even", 
    "evenk", 
    "ewe", 
    "extremaduran", 
    "faroese language", 
    "fang", 
    "fijian", 
    "filipino", 
    "finnish", 
    "finnish sign language", 
    "flemish language", 
    "fon", 
    "franco-proven\u00e7al", 
    "french", 
    "french sign language", 
    "frisian, north", 
    "frisian, saterland", 
    "frisian, west", 
    "friulian", 
    "fula", 
    "fur", 
    "ga", 
    "gadaba", 
    "gagauz", 
    "galician", 
    "gallo", 
    "gan", 
    "ganda", 
    "gangte", 
    "garhwali", 
    "gayo", 
    "gen", 
    "georgian", 
    "german", 
    "german sign language", 
    "gikuyu", 
    "gilbertese", 
    "gileki", 
    "goaria", 
    "gondi", 
    "gorani", 
    "gowro", 
    "gawar-bati", 
    "greek", 
    "guaran\u00ed", 
    "guinea-bissau creole", 
    "gujarati", 
    "gula iro", 
    "gullah", 
    "gusii", 
    "gwich\u02bcin", 
    "hadza", 
    "haida", 
    "haitian creole", 
    "hakka", 
    "h\u00e4n", 
    "harari", 
    "harauti", 
    "harsusi", 
    "haryanavi", 
    "harzani", 
    "hausa", 
    "havasupai", 
    "hawaiian", 
    "hawaii pidgin sign language", 
    "hazaragi", 
    "hebrew", 
    "herero", 
    "h\u00e9rtevin", 
    "hiligaynon", 
    "hindi", 
    "hinukh", 
    "hiri motu", 
    "hixkaryana", 
    "hmong", 
    "ho", 
    "hoby\u00f3t", 
    "hopi", 
    "hulaul\u00e1", 
    "hungarian", 
    "hunsrik", 
    "hutterite german", 
    "ibibio", 
    "iban", 
    "ibanag", 
    "icelandic", 
    "ido", 
    "if\u00e8", 
    "igbo", 
    "ikalanga", 
    "ili turki", 
    "ilokano", 
    "inari sami", 
    "indonesian", 
    "ingrian", 
    "ingush", 
    "interlingua", 
    "inuktitut", 
    "inupiaq", 
    "inuvialuktun", 
    "iraqw", 
    "irish", 
    "irish sign language", 
    "irula", 
    "isan", 
    "ishkashimi", 
    "istro-romanian", 
    "italian", 
    "itelmen", 
    "jacaltec", 
    "jalaa", 
    "japanese", 
    "jaqaru", 
    "jarai", 
    "javanese", 
    "jibbali", 
    "jewish babylonian aramaic", 
    "jicarilla apache", 
    "juang", 
    "jurchen", 
    "kabardian", 
    "kabyle", 
    "kachin", 
    "kalaallisut", 
    "kalami", 
    "kalasha", 
    "kalmyk", 
    "kalto", 
    "kankanai", 
    "kannada", 
    "kaonde", 
    "kapampangan", 
    "karachay-balkar", 
    "karagas", 
    "karaim", 
    "karakalpak", 
    "karelian", 
    "kashmiri", 
    "kashubian", 
    "kazakh", 
    "kerek", 
    "ket", 
    "khakas", 
    "khalaj", 
    "kham", 
    "khandeshi", 
    "khanty", 
    "khasi", 
    "khitan", 
    "khmer", 
    "khmu", 
    "khowar", 
    "kildin sami", 
    "kimatuumbi", 
    "kinaray-a", 
    "kinyarwanda", 
    "kirombo", 
    "kirundi", 
    "kivunjo", 
    "klallam", 
    "kodava takk", 
    "kohistani", 
    "kolami", 
    "komi", 
    "konkani", 
    "kongo", 
    "koraga", 
    "korandje", 
    "korean", 
    "korku", 
    "korowai", 
    "korwa", 
    "koryak", 
    "kosraean", 
    "kota", 
    "koyra chiini", 
    "koy sanjaq surat", 
    "koya", 
    "krymchak", 
    "kujarge", 
    "kui", 
    "kumauni", 
    "kumyk", 
    "kumzari", 
    "\u01c3kung", 
    "kurdish", 
    "kurukh", 
    "kusunda", 
    "kutenai", 
    "kwanyama", 
    "kxoe", 
    "kyrgyz", 
    "laal", 
    "ladakhi", 
    "ladin", 
    "ladino", 
    "laki", 
    "lakota", 
    "lambadi", 
    "lao", 
    "larestani", 
    "latin", 
    "latvian", 
    "laz", 
    "leonese", 
    "lepcha", 
    "lezgi", 
    "ligbi", 
    "limbu", 
    "limburgish", 
    "lingala", 
    "lipan apache", 
    "lisan al-dawat", 
    "lishana deni", 
    "lishanid noshan", 
    "lithuanian", 
    "livonian language", 
    "lombard", 
    "lotha", 
    "low german", 
    "lower sorbian", 
    "lozi", 
    "ludic", 
    "lunda", 
    "luo", 
    "luri", 
    "lushootseed", 
    "lusoga", 
    "luvale", 
    "luwati", 
    "luxembourgish", 
    "lycian", 
    "lydian", 
    "macedonian", 
    "magadhi", 
    "maguindanao", 
    "maithili", 
    "makasar", 
    "makhuwa", 
    "makhuwa-meetto", 
    "malagasy", 
    "malay", 
    "malayalam", 
    "malaysian sign language", 
    "maltese", 
    "malto", 
    "malvi", 
    "mam", 
    "manchu", 
    "mandaic", 
    "mandarin", 
    "mandinka", 
    "mansi", 
    "manx", 
    "manyika", 
    "maori", 
    "mapudungun", 
    "maranao", 
    "marathi", 
    "mari", 
    "maria", 
    "marquesan", 
    "marshallese", 
    "martha's vineyard sign language", 
    "masaba", 
    "masbatenyo", 
    "meitei", 
    "mauritian creole", 
    "maya", 
    "mazandarani", 
    "me\u00e4nkieli", 
    "megleno-romanian", 
    "megrelian", 
    "mehri", 
    "menominee", 
    "mentawai", 
    "meroitic", 
    "mescalero apache", 
    "meru", 
    "michif", 
    "mikasuki", 
    "mi'kmaq", 
    "minangkabau", 
    "mirandese", 
    "mobilian jargon", 
    "moghol", 
    "mohawk", 
    "moksha", 
    "molengue", 
    "mon", 
    "mongolian", 
    "mono", 
    "mono", 
    "mono", 
    "montagnais", 
    "montenegrin", 
    "motu", 
    "muher", 
    "mundari", 
    "munji", 
    "muria", 
    "nafaanra", 
    "nagarchal", 
    "nahuatl", 
    "nama", 
    "nanai", 
    "nauruan", 
    "navajo", 
    "ndau", 
    "ndebele", 
    "ndonga", 
    "neapolitan", 
    "negidal", 
    "nepal bhasa", 
    "nepali", 
    "new zealand sign language", 
    "nihali", 
    "nganasan", 
    "ngumba", 
    "nheengatu", 
    "nias", 
    "nicaraguan sign language", 
    "niellim", 
    "nigerian pidgin", 
    "nisenan", 
    "niuean", 
    "nivkh", 
    "nogai", 
    "norfuk", 
    "norman", 
    "northern sami", 
    "northern sotho", 
    "northern straits salish)", 
    "northern yukaghir", 
    "norwegian", 
    "nuer", 
    "nux\u00e1lk", 
    "nyabwa", 
    "nyah kur", 
    "nyangumarta", 
    "nyoro", 
    "n\u01c0u", 
    "occitan", 
    "ojibwe", 
    "okinawan", 
    "olonets karelian", 
    "omagua", 
    "ongota", 
    "odia", 
    "ormuri", 
    "oroch", 
    "orok", 
    "oromo", 
    "ossetic", 
    "old east slavic", 
    "old prussian", 
    "p\u00e1ez", 
    "palauan", 
    "pangasinan", 
    "papiamento", 
    "parachi", 
    "parya", 
    "pashto", 
    "pennsylvania dutch", 
    "persian", 
    "phalura", 
    "phuthi", 
    "pig latin", 
    "picard", 
    "pirah\u00e3", 
    "plautdietsch", 
    "polish", 
    "portuguese", 
    "pothohari", 
    "pradhan", 
    "puelche", 
    "puma", 
    "punjabi", 
    "qashqai", 
    "quebec sign language", 
    "quechua", 
    "rajasthani", 
    "ratagnon", 
    "r\u00e9union creole", 
    "romanian", 
    "romansh", 
    "romany", 
    "romblomanon", 
    "rotokas", 
    "runyankole language", 
    "russian", 
    "russian sign language", 
    "ruthenian", 
    "sadri", 
    "salar", 
    "samoan", 
    "sandawe", 
    "sango", 
    "sanskrit", 
    "santali", 
    "sara", 
    "saraiki", 
    "saramaccan", 
    "sardinian", 
    "sarikoli", 
    "standard arabic", 
    "saurashtra", 
    "savara", 
    "savi", 
    "sawai", 
    "scots", 
    "scots gaelic", 
    "selangor sign language", 
    "selkup", 
    "semnani", 
    "senaya", 
    "serbian", 
    "serbo-croatian", 
    "sesotho", 
    "seto", 
    "seychellois creole", 
    "shimaore", 
    "shina", 
    "shona", 
    "shor", 
    "shoshoni", 
    "shughni", 
    "shumashti", 
    "shuswap", 
    "sicilian", 
    "sidamo", 
    "sika", 
    "silesian", 
    "silt'e", 
    "sindhi", 
    "sinhalese", 
    "sioux", 
    "sivandi", 
    "skolt sami", 
    "slavey", 
    "slovak", 
    "slovene", 
    "soddo", 
    "somali", 
    "sonjo", 
    "sonsorolese", 
    "soqotri", 
    "sora", 
    "sorbian, lower", 
    "sorbian, upper", 
    "sourashtra", 
    "southern sami", 
    "south estonian", 
    "southern yukaghir", 
    "spanish", 
    "sranan tongo", 
    "st'at'imcets", 
    "sucite", 
    "suba", 
    "sundanese", 
    "supyire", 
    "surigaonon", 
    "susu", 
    "svan", 
    "swahili", 
    "swati", 
    "swedish", 
    "syriac", 
    "tabasaran", 
    "tachelhit", 
    "tagalog", 
    "tahitian", 
    "taiwanese sign language", 
    "tajik", 
    "takestani", 
    "talysh", 
    "tamil", 
    "tanacross", 
    "tangut", 
    "tarifit", 
    "tat", 
    "tatar", 
    "tausug", 
    "tehuelche", 
    "telugu", 
    "tetum", 
    "tepehua language", 
    "tepehu\u00e1n language", 
    "thai", 
    "tharu", 
    "tibetan", 
    "tigre", 
    "tigrinya", 
    "timbisha", 
    "tiv", 
    "tlingit", 
    "tobian", 
    "toda", 
    "tok pisin", 
    "tokelauan", 
    "tonga", 
    "tongan", 
    "torwali", 
    "tregami", 
    "tsat", 
    "tsez", 
    "tshiluba", 
    "tsonga", 
    "tswana", 
    "tu", 
    "tuareg languages", 
    "tulu", 
    "tumbuka", 
    "tupiniquim", 
    "turkish", 
    "turkmen", 
    "turoyo", 
    "tuvaluan", 
    "tuvan tuvin", 
    "udihe", 
    "udmurt", 
    "ukrainian", 
    "ukwuani-aboh-ndoni", 
    "ulch", 
    "unserdeutsch", 
    "upper sorbian", 
    "urdu", 
    "uripiv", 
    "urum", 
    "ute", 
    "uyghur", 
    "uzbek", 
    "vafsi", 
    "valencian", 
    "valencian sign language", 
    "vasi-vari", 
    "venda", 
    "venetian", 
    "veps", 
    "vietnamese", 
    "v\u00f5ro", 
    "votic", 
    "waddar", 
    "waigali", 
    "waima", 
    "wakhi", 
    "walloon", 
    "waray-waray", 
    "washo", 
    "welsh", 
    "western neo-aramaic", 
    "wolane", 
    "wolof", 
    "wu", 
    "xhosa", 
    "xiang", 
    "xibe", 
    "xipaya", 
    "x\u00f3\u00f5", 
    "yaaku language", 
    "yaeyama language", 
    "yaghnobi", 
    "yakut", 
    "yankunytjatjara language", 
    "yanomami", 
    "yanyuwa", 
    "yapese", 
    "yaqui", 
    "yauma", 
    "yavapai", 
    "yazdi", 
    "yazgulyam", 
    "yemenite hebrew", 
    "yeni language", 
    "yevanic language", 
    "yi language", 
    "yiddish", 
    "yidgha", 
    "yogur", 
    "yokutsan languages", 
    "yonaguni language", 
    "yoruba language", 
    "yucatec maya language", 
    "yucatec maya sign language", 
    "yuchi language", 
    "yugur", 
    "yukaghir languages", 
    "yupik language", 
    "yurats language", 
    "yurok language", 
    "z\u00e1paro", 
    "zapotec", 
    "zazaki", 
    "zulu", 
    "zu\u00f1i", 
    "zway"
]

languages_de = [
    "aari",
    "abanyom",
    "abasa",
    "abchasisch",
    "abujmaria",
    "aceh",
    "adamorobe zeichensprache",
    "adele",
    "adygeisch",
    "afar",
    "afrikaans",
    "afro-seminole-kreolisch",
    "aimaq",
    "aini",
    "ainu",
    "akan",
    "akawaio",
    "aklanon",
    "albanisch",
    "aleutisch",
    "algonkin",
    "elsässisch",
    "altaisch",
    "alutor",
    "amerikanische gebärdensprache",
    "amharisch",
    "anda",
    "amdang",
    "altes meitei",
    "angika",
    "anyin",
    "ao",
    "a-pucikwar",
    "arabisch",
    "aragonesisch",
    "aramäisch",
    "are",
    "'are'are",
    "argobba",
    "aromunisch",
    "armenisch",
    "arvanitisch",
    "ashkun",
    "asi",
    "assamesisch",
    "neuostaramäisch",
    "asturisch",
    "ateso",
    "a'tong",
    "'auhelawa",
    "australische zeichensprache",
    "bairisch",
    "awarisch",
    "avestisch",
    "awadhi",
    "aymara",
    "aserbaidschanisch",
    "badaga",
    "badeshi",
    "bahnar",
    "balinesisch",
    "belutschisch",
    "balti",
    "bambara",
    "banjar",
    "banyumasan",
    "bartangi",
    "basaa",
    "bashkardi",
    "baschkirisch",
    "baskisch",
    "batak Karo",
    "batak Toba",
    "batsisch",
    "bedscha",
    "belarussisch",
    "belhare",
    "berta",
    "bemba",
    "bengalisch",
    "bezhta",
    "betawi",
    "bete",
    "bhili",
    "bhojpuri",
    "bijil neo-aramäisch",
    "bikol",
    "bikya",
    "bissa",
    "schwarzfuß",
    "boholano",
    "bohtan neo-aramäisch",
    "bonan",
    "bororo",
    "bodo",
    "bosnisch",
    "brahui",
    "bretonisch",
    "britische gebärdensprache",
    "bua",
    "buginesisch",
    "bukusu",
    "bulgarisch",
    "bunjewatzisch",
    "birmanisch",
    "burushaski",
    "burjatisch",
    "caddo",
    "cahuilla",
    "caluyanon",
    "kantonesisch",
    "katalanisch",
    "cayuga",
    "cebuano",
    "chabacano",
    "chaga",
    "chakma",
    "chaldäisches neu-aramäisch",
    "chamorro",
    "chaouia",
    "cschetschenisch",
    "chenchu",
    "chenoua",
    "cherokee",
    "cheyenne",
    "chhattisgarhi",
    "chickasaw",
    "chintang",
    "chilcotin",
    "chinesisch",
    "chiricahua",
    "chichewa",
    "chipewyan",
    "chittagonisch",
    "choctaw",
    "chorasmisch",
    "tschuktschisch",
    "tschulym",
    "kirchenslawisch",
    "chuukesisch",
    "tschuwaschisch",
    "cocoma",
    "cocopa",
    "coeur d'alene",
    "komantschisch",
    "komorisch",
    "kornisch",
    "korsisch",
    "cree",
    "krimtatarisch",
    "kroatisch",
    "cuyonon",
    "tschechisch",
    "dagbani",
    "dahlik",
    "dalmål",
    "dameli",
    "dänisch",
    "darginisch",
    "dakota",
    "dari",
    "dari-oersisch",
    "daurisch",
    "dena'ina",
    "dhatki",
    "dhivehi",
    "dida",
    "dioula",
    "dogri",
    "dogrib",
    "dolganisch",
    "domaaki",
    "dongxiang",
    "duala",
    "dunganisch",
    "niederländisch",
    "dzhidi",
    "dzongkha",
    "ostjughurisch",
    "edo",
    "efik",
    "esan",
    "ägyptisch-arabisch",
    "ekoti",
    "enzisch",
    "englisch",
    "erza-mordwinisch",
    "esperanto",
    "estnisch",
    "ewenisch",
    "ewenkisch",
    "ewe",
    "extremadurisch",
    "färöisch",
    "fang",
    "fidschianisch",
    "filipino",
    "finnisch",
    "finnische Gebärdensprache",
    "flämisch",
    "fon",
    "frankoprovenzalisch",
    "französisch",
    "französische Gebärdensprache",
    "nordfriesisch",
    "saterfriesisch",
    "westfriesisch",
    "friaulisch",
    "fulfulde",
    "fur",
    "ga",
    "gadaba",
    "gagausisch",
    "galicisch",
    "gallo",
    "gan",
    "luganda",
    "gangte",
    "garhwali",
    "gayo",
    "gen",
    "georgisch",
    "deutsch",
    "deutsche gebärdensprache",
    "kikuyu",
    "gilbertesisch",
    "gilaki",
    "goaria",
    "gondi",
    "gorani",
    "gowro",
    "gawar-bati",
    "griechisch",
    "guaraní",
    "guinea-bissau-kreol",
    "gujarati",
    "gula iro",
    "gullah",
    "gusii",
    "gwich’in",
    "hadza",
    "haida",
    "haitianisches kreol",
    "hakka",
    "hän",
    "harari",
    "harauti",
    "harsusi",
    "haryanvi",
    "harzani",
    "hausa",
    "havasupai",
    "hawaiianisch",
    "hawaii pidgin gebärdensprache",
    "hazaragi",
    "hebräisch",
    "herero",
    "hértevin",
    "hiligaynon",
    "hindi",
    "hinukh",
    "hiri motu",
    "hixkaryana",
    "hmong",
    "ho",
    "hobyót",
    "hopi",
    "hulaulá",
    "ungarisch",
    "hunsrik",
    "hutterisch",
    "ibibio",
    "iban",
    "ibanag",
    "isländisch",
    "ido",
    "ifè",
    "igbo",
    "ikalanga",
    "ili turki",
    "ilokano",
    "inarisamisch",
    "indonesisch",
    "ingrisch",
    "inguschisch",
    "interlingua",
    "inuktitut",
    "inupiaq",
    "inuvialuktun",
    "iraqw",
    "irisch",
    "irische gebärdensprache",
    "irula",
    "isan",
    "ishkashimi",
    "istrorumänisch",
    "italienisch",
    "itelmenisch",
    "jakaltekisch",
    "jalaa",
    "japanisch",
    "jaqaru",
    "jarai",
    "javanisch",
    "jibbali",
    "jüdisch-babylonisches aramäisch",
    "jicarilla-apache",
    "juang",
    "jurchen",
    "kabardinisch",
    "kabylisch",
    "kachin",
    "grönländisch",
    "kalami",
    "kalasha",
    "kalmückisch",
    "kalto",
    "kankanai",
    "kannada",
    "kaonde",
    "kapampangan",
    "karatschai-balkarisch",
    "karagas",
    "karaimisch",
    "karakalpakisch",
    "karelianisch",
    "kaschmirisch",
    "kaschubisch",
    "kasachisch",
    "kerek",
    "ketisch",
    "chakassisch",
    "khalaj",
    "kham",
    "khandeshi",
    "chanten",
    "khasi",
    "kitaisch",
    "khmer",
    "khmu",
    "khowar",
    "kildin-samisch",
    "kimatuumbi",
    "kinaray-a",
    "kinyarwanda",
    "kirombo",
    "kirundi",
    "kivunjo",
    "klallam",
    "kodava",
    "kohistani",
    "kolami",
    "komi",
    "konkani",
    "kongo",
    "koraga",
    "korandje",
    "koreanisch",
    "korku",
    "korowai",
    "korwa",
    "koriakisch",
    "kosraeanisch",
    "kota",
    "koyra chiini",
    "koy sanjaq surat",
    "koya",
    "krimtschakisch",
    "kujarge",
    "kui",
    "kumauni",
    "kumykisch",
    "kumzari",
    "kung",
    "kurdisch",
    "kurukh",
    "kusunda",
    "kutenai",
    "kwanyama",
    "kxoe",
    "kirgisisch",
    "laal",
    "ladakhi",
    "ladinisch",
    "ladino",
    "laki",
    "lakota",
    "lambadi",
    "laotisch",
    "larestani",
    "latein",
    "lettisch",
    "lasisch",
    "leonisch",
    "lepcha",
    "lesgisch",
    "ligbi",
    "limbu",
    "limburgisch",
    "lingala",
    "lipan-apache",
    "lisan al-dawat",
    "lishana deni",
    "lishanid noshan",
    "litauisch",
    "livisch",
    "lombardisch",
    "lotha",
    "plattdeutsch",
    "niedersorbisch",
    "lozi",
    "ludisch",
    "lunda",
    "luo",
    "luri",
    "lushootseed",
    "lusoga",
    "luvale",
    "luwati",
    "luxemburgisch",
    "lykisch",
    "lydisch",
    "mazedonisch",
    "magadhi",
    "maguindanao",
    "maithili",
    "makassarisch",
    "makhuwa",
    "makhuwa-meetto",
    "madagassisch",
    "malaiisch",
    "malayalam",
    "malaysische gebärdensprache",
    "maltesisch",
    "malto",
    "malvi",
    "mam",
    "mandschurisch",
    "mandäisch",
    "mandarin",
    "mandinka",
    "mansisch",
    "manx",
    "manyika",
    "maori",
    "mapudungun",
    "maranao",
    "marathi",
    "mari",
    "maria",
    "marquesanisch",
    "marshallisch",
    "martha's vineyard gebärdensprache",
    "masaba",
    "masbatenyo",
    "meitei",
    "mauritius-kreolisch",
    "maya",
    "masanderanisch",
    "meänkieli",
    "meglenitisch",
    "mingrelisch",
    "mehri",
    "menominee",
    "mentawai",
    "meroitisch",
    "mescalero-apache",
    "meru",
    "michif",
    "mikasuki",
    "mi'kmaq",
    "minangkabau",
    "mirandesisch",
    "mobilianischer jargon",
    "moghol",
    "mohawk",
    "mokschanisch",
    "molengue",
    "mon",
    "mongolisch",
    "mono (demokratische republik kongo)",
    "mono (usa)",
    "mono (salomonen)",
    "montagnais",
    "montenegrinisch",
    "motu",
    "muher",
    "mundari",
    "munji",
    "muria",
    "nafaanra",
    "nagarchal",
    "nahuatl",
    "nama",
    "nanai",
    "nauruisch",
    "navajo",
    "ndau",
    "nNdebele",
    "ndonga",
    "neapolitanisch",
    "negidalisch",
    "newari",
    "nepalesisch",
    "neuseeländische gebärdensprache",
    "nihali",
    "nganasanisch",
    "ngumba",
    "nheengatu",
    "nias",
    "nicaraguanische gebärdensprache",
    "niellim",
    "nigerianisches pidgin",
    "nisenan",
    "niueanisch",
    "nivkh",
    "nogaisch",
    "norfuk (norfolk)",
    "normannisch",
    "nordsamisch",
    "nord-Sotho",
    "nördliches straits-salish",
    "nördliches jukagirisch",
    "norwegisch",
    "nuer",
    "nuxálk",
    "nyabwa",
    "nyah kur",
    "nyangumarta",
    "nyoro",
    "nǀuu",
    "okzitanisch",
    "ojibwe",
    "okinawanisch",
    "olonezisch-karelisch",
    "omagua",
    "ongota",
    "odia",
    "ormuri",
    "orotsch",
    "uilta (orok)",
    "oromo",
    "ossetisch",
    "altrussisch",
    "altpreußisch",
    "páez",
    "palauisch",
    "pangasinan",
    "papiamento",
    "parachi",
    "parya",
    "paschtu",
    "pennsylvania-deutsch",
    "persisch",
    "phalura",
    "phuthi",
    "pig latin",
    "pikardisch",
    "pirahã",
    "plautdietsch",
    "polnisch",
    "portugiesisch",
    "pothohari",
    "pradhan",
    "puelche",
    "puma",
    "punjabi",
    "qashqai",
    "quebecer gebärdensprache",
    "quechua",
    "rajasthani",
    "ratagnon",
    "réunion-kreolisch",
    "rumänisch",
    "rätoromanisch",
    "romani",
    "romblomanon",
    "rotokas",
    "runyankore",
    "russisch",
    "russische gebärdensprache",
    "ruthenisch",
    "sadri",
    "salar",
    "samoanisch",
    "sandawe",
    "sango",
    "sanskrit",
    "santali",
    "sara",
    "saraiki",
    "saramaccaans",
    "sardisch",
    "sarikoli",
    "hocharabisch",
    "savara",
    "savi",
    "sawai",
    "schottisch",
    "schottisches gälisch",
    "selangor-zeichensprache",
    "selkupisch",
    "semnani",
    "senaya",
    "serbisch",
    "serbokroatisch",
    "sesotho",
    "seto",
    "seychellen-kreol",
    "shimaore",
    "shina",
    "shona",
    "schorisch",
    "shoshoni",
    "schugni",
    "shumashti",
    "shuswap",
    "sizilianisch",
    "sidamo",
    "sika",
    "schlesisch",
    "silt'e",
    "sindhi",
    "singhalesisch",
    "sioux",
    "sivandi",
    "skoltsamisch",
    "slavey",
    "slowakisch",
    "slowenisch",
    "soddo",
    "somali",
    "sonjo",
    "sonsorolesisch",
    "soqotri",
    "sora",
    "niedersorbisch",
    "obersorbisch",
    "sourashtra",
    "südsamisch",
    "südestnisch",
    "süd-jukagirisch",
    "spanisch",
    "sranan tongo",
    "st'at'imcets",
    "sucite",
    "suba",
    "sundanesisch",
    "supyire",
    "surigaonon",
    "susu",
    "swanisch",
    "swahili",
    "swati",
    "schwedisch",
    "syrisch",
    "tabassaranisch",
    "tachelhit",
    "tagalog",
    "tahitianisch",
    "taiwanische gebärdensprache",
    "tadschikisch",
    "takestani",
    "talyschisch",
    "tamil",
    "tanacross",
    "tangut",
    "tarifit",
    "tatisch",
    "tataren",
    "tausūg",
    "tehuelche",
    "telugu",
    "tetum",
    "tepehua",
    "tepehuán",
    "thailändisch",
    "tharu",
    "tibetisch",
    "tigre",
    "tigrinya",
    "timbisha",
    "tiv",
    "tlingit",
    "tobianisch",
    "toda",
    "tok Pisin",
    "tokelauisch",
    "tonga",
    "tonganisch",
    "torwali",
    "tregami",
    "tsat",
    "tsesisch",
    "tschiluba",
    "tsonga",
    "tswana",
    "tu",
    "tuareg-sprachen",
    "tulu",
    "tumbuka",
    "tupiniquim",
    "türkisch",
    "turkmenisch",
    "turoyo",
    "tuvaluisch",
    "tuwinisch",
    "udihe",
    "udmurtisch",
    "ukrainisch",
    "ukwuani-aboh-noni",
    "ultschisch",
    "unserdeutsch",
    "obersorbisch",
    "urdu",
    "uripiv",
    "urum",
    "ute",
    "uigurisch",
    "usbekisch",
    "vafsi",
    "valencianisch",
    "valencianische gebärdensprache",
    "vasi-vari",
    "venda",
    "venezianisch",
    "wepsisch",
    "vietnamesisch",
    "võro",
    "wotisch",
    "waddar",
    "waigali",
    "waima",
    "wakhi",
    "wallonisch",
    "waray",
    "washo",
    "walisisch",
    "westliches neuaramäisch",
    "wolane",
    "wolof",
    "wu",
    "xhosa",
    "xiang",
    "sibe",
    "xipaya",
    "xóõ",
    "yaaku",
    "yaeyama",
    "yaghnobi",
    "jakutisch",
    "yankunytjatjara",
    "yanomami",
    "yanyuwa",
    "yapesisch",
    "yaqui",
    "yauma",
    "yavapai",
    "yazdi",
    "yazgulyam",
    "jemenitisches hebräisch",
    "yeni",
    "yevanisch",
    "yi",
    "jiddisch",
    "yidgha",
    "yogur",
    "yokutsan",
    "yonaguni",
    "yoruba",
    "yucatekisches maya",
    "yucatekische maya-gebärdensprache",
    "yuchi",
    "yugur",
    "jukagirisch",
    "yupik",
    "yurats",
    "yurok",
    "záparo",
    "zapotekisch",
    "zazaki",
    "zulu",
    "zuni",
    "zway"
]
languages_all = set(languages_en) | set(languages_de)


def get_city_country(url, city, country, lang='de'):
    # print(url, city, country, lang)
    city_normalized, country_normalized = "", ""
    if not lang:
        lang = 'de'
    try:
        
        if city:
            url_request = f"{url}/api?q={city}&lang={lang}&limit=3&bbox=-27.627108,33.036997,65.029825,70.750216" 
        else:
            url_request = f"{url}/api?q={country}&lang={lang}&limit=3&bbox=-27.627108,33.036997,65.029825,70.750216"
                  
        response = requests.get(url_request)
        data = response.json()
        found_city = False

        for feature in data['features']:
            data_properties = feature['properties']
    
            if data_properties['type'] == 'city' and not found_city:
                city_normalized = data_properties['name']
                country_normalized = data_properties['country'] 
                found_city = True  
                break  
    
            elif data_properties['type'] == 'country' and not found_city:
                country_normalized = data_properties['country'] 
                break  

    except Exception as e:
        print(f"Error fetching data for city: {city}, country: {country}: {e}")

    return city_normalized, country_normalized

class GptOutput(BaseModel):
    jobTitle: Optional[List[str]] = None
    city: Optional[str] = None
    country: Optional[str] = None
    radius: Optional[int] = 0
    mandatorySkills: Optional[List[str]] = None
    optionalSkills: Optional[List[str]] = None
    mandatoryLanguages: Optional[List[str]] = None
    optionalLanguages: Optional[List[str]] = None
    # suggestions: bool = False
    yearsOfExperienceFrom: Optional[int] = 0
    yearsOfExperienceTo: Optional[int] = 0
    yearsInJobFrom: Optional[int] = 0
    yearsInJobTo: Optional[int] = 0
    email: Optional[bool] = False
    phone: Optional[bool] = False
    worksAt: Optional[List[str]] = None
    doesNotWorkAt: Optional[List[str]] = None
    previouslyWorkedAt: Optional[List[str]] = None
    doesNotPreviouslyWorkAt: Optional[List[str]] = None
    personIs: Optional[List[str]] = None
    personIsNot: Optional[List[str]] = None
    previouslyAs: Optional[str] = None
    doesNotPreviouslyWorkAs: Optional[str] = None
    lang: Optional[str] = 'en'
    level: Optional[str] = None
    industry: Optional[str] = None
    jobTitleSuggestions: Optional[List[str]] = None
    skillsSuggestions: Optional[List[str]] = None
    
    @validator('jobTitle', pre=True, always=True)
    def set_default_for_job_title(cls, v):
        if v is None:
            return []
        return v
    
    @validator('mandatorySkills', pre=True, always=True)
    def set_default_for_mandatory_skills(cls, v):
        if v is None:
            return []
        return v
    
    @validator('optionalSkills', pre=True, always=True)
    def set_default_for_optional_skills(cls, v):
        if v is None:
            return []
        return v
    
    @validator('mandatoryLanguages', pre=True, always=True)
    def set_default_for_mandatory_languages(cls, v):
        if v is None:
            return []
        return v
    
    @validator('optionalLanguages', pre=True, always=True)
    def set_default_for_optional_languages(cls, v):
        if v is None:
            return []
        return v
    
    @validator('personIs', pre=True, always=True)
    def set_default_for_person_is(cls, v):
        if v is None:
            return []
        return v
    
    @validator('personIsNot', pre=True, always=True)
    def set_default_for_person_is_not(cls, v):
        if v is None:
            return []
        return v

    @validator('worksAt', pre=True, always=True)
    def set_default_for_works_at(cls, v):
        if v is None:
            return []
        return v
    
    @validator('doesNotWorkAt', pre=True, always=True)
    def set_default_for_does_not_works_at(cls, v):
        if v is None:
            return []
        return v
    
    @validator('previouslyWorkedAt', pre=True, always=True)
    def set_default_for_previously_worked_at(cls, v):
        if v is None:
            return []
        return v
    
    @validator('doesNotPreviouslyWorkAt', pre=True, always=True)
    def set_default_for_does_not__previously_worked_at(cls, v):
        if v is None:
            return []
        return v
    
    @validator('jobTitleSuggestions', pre=True, always=True)
    def set_default_for_job_title_suggestions(cls, v):
        if v is None:
            return []
        return v
    
    @validator('skillsSuggestions', pre=True, always=True)
    def set_default_for_skills_suggestions(cls, v):
        if v is None:
            return []
        return v
    
    class Config:
        extra = Extra.ignore
        
        
def clean_json_output(generated_text: str) -> str:
    try:
        start_idx = generated_text.index('{')
        end_idx = generated_text.rindex('}') + 1
        json_text = generated_text[start_idx:end_idx]
        return json_text
    except ValueError as e:
        print(f"Error in finding JSON boundaries: {e}")
        return "{}"
    
def parse_gpt_output(generated_text: str) -> GptOutput:
    cleaned_text = clean_json_output(generated_text)
    try:
        data = json.loads(cleaned_text)
        return GptOutput(**data)
    except json.JSONDecodeError as e:
        print(f"Error in parsing the JSON output: {e}")
        return GptOutput()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return GptOutput()
    
system_instruction = """
You are an assistant tasked with extracting specific information from user inputs where applicable. Follow these instructions carefully to extract and structure the required details.
 
Extraction Requirements:
1. Job Title:
    a) Extract the job titles mentioned in the user input.
    b) Exclude any gender-related terms (e.g., m/f/d, w/m/d).
    c) Format as a list.
    d) When dealing with German job titles, always include gender variations. For example, if a job title is "Software Engineer," add "Software Engineerin" as well. Ensure this gender normalization is only applied to German job titles and not to English titles that do not require it (e.g., "Sales Representative" should not be altered).
    e) YOU MUST ENSURE THAT YOU ADD TO THE JOB TITLE GERMAN GENDER VARIATION IF IT EXISTS (NO MATTER OF LANGUAGE)! 
    Example: If the user inputs "Software Engineer," you should return ["Software Engineer", "Software Engineerin"].
 
2. City:
    a) Extract the city related to the job position.
    b) Maintain the original language (fix typos if necessary).
    c) Do not translate the city name.
 
3. Country:
    a) Extract the country related to the job position.
    b) Maintain the original language (fix typos if necessary).
    c) Do not translate the country name.
 
4. Radius:
    a) Extract the distance to the location specified.
    b) Format as a numerical value.
 
5. Mandatory Skills:
    a) Extract key skills required for the role.
    b) Provide shorter versions of the skills (e.g., 'python' instead of 'Python programming language').
 
6. Optional Skills:
    a) Extract desirable skills that are beneficial for the role.
    b) Provide shorter versions of the skills (e.g., 'python' instead of 'Python programming language').
    c) Educational level if mentioned add as skill (e.g., 'Master's degree' then add 'Master's degree' as well)
    d) For educational level add if makes sense the field of study (e.g., 'Master's degree in Computer Science' then add 'Computer Science' as well)
 
7. Languages Required:
    a) Extract the languages required for the role.
    b) Format as two lists (mandatory and optional languages).
 
8. Years of Experience Required:
    a) Extract the required years of experience.
    b) Specify as a range (from minimum to maximum).
 
9. Years in Job:
    a) Extract the number of years the person should have been in the current job position.
    b) Specify as a range (from minimum to maximum).
 
10. Email:
    a) Indicate whether an email address is required in the applicant's profile.
    b) Format as a boolean (true or false).
 
11. Phone:
    a) Indicate whether a phone number is required in the applicant's profile.
    b) Format as a boolean (true or false).
 
12. Company Preferences:
    a) Extract preferences for company names. Categories:
        - worksAt: List of preferred companies.
        - doesNotWorkAt: List of companies to avoid.
        - previouslyWorkedAt: List of companies the applicant has worked at before.
        - doesNotPreviouslyWorkAt: List of companies the applicant should not have worked at before.
    b) Exclude industry mentions.
    c) Exclude words startup, start-up and 'start up' as it is not considered as a company name. (e.g. previously worked at a startup should not be considered as a company name)
    d) DO NOT ADD STARTUP, START UP, START-UP AS A COMPANY NAME!
 
13. Person Is:
    a) From the job description, identify if any of the following descriptors are explicitly mentioned: 'Consultant', 'Executive', 'Freelancer', 'Scientist', 'Student'.
    b) If a descriptor is mentioned, include it in the personIs list.
    c) Format the extracted descriptors as a list.
    d) If the user is looking for data scientist, do not add 'Scientist' as a personIs descriptor.
 
14. Person Is Not:
    a) Extract descriptors the person should not be (e.g., 'Consultant', 'Executive', 'Freelancer', 'Scientist', 'Student').
    b) Format as a list based on user input.
 
15. Previously As:
    a) Extract the previous job title if mentioned.
    b) Format as a string.
 
16. Does Not Previously Work As:
    a) Specify the job title the person should not have previously worked as.
    b) Format as a string.
 
17. Industry:
    a) Extract the sector or field of the job position. The only options are: 'Agriculture', 'Architecture and Planning', 'Arts and Culture', 'Audit, Tax and Legal', 'Automotive', 'Aviation and Aerospace', 'Banks and Financial Services', 'Chemicals', 'Construction', 'Consultancy', 'Consumer Goods and Retail', 'Education, Training and Science', 'Energy, Water and Environment', 'Entertainment', 'Gambling and Casinos', 'Health and Wellness', 'HR Services', 'Industrial and Mechanical Engineering', 'Insurance', 'IT and Internet', 'Leisure, Tourism and Gastronomy', 'Marketing, PR and Design', 'Media and Publishing', 'Pharmaceuticals', 'Public Service, Federations and Institutions', 'Real Estate', 'Sport', 'Telecommunication', 'Transport and Logistics', 'Other Sectors'
    b) German names of the industries are also allowed and here is their list: 'Architektur und Planung', 'Automobil', 'Banken und Finanzdienstleistungen', 'Beratung und Consulting', 'Chemieindustrie', 'Energie, Wasser und Umwelt', 'Erziehung, Bildung und Wissenschaft', 'Freizeit, Tourismus und Gastronomie', 'Gambling and Casinos', 'Gesundheit und Wellness', 'Immobilien', 'Industrie und Maschinenbau', 'Internet und Informationstechnologie', 'Konstruktion', 'Konsumgüter und Handel', 'Kunst und Kultur', 'Landwirtschaft', 'Luft- und Raumfahrt', 'Marketing, PR und Design', 'Medien und Verlage', 'Öffentlicher Dienst, Verbände und Einrichtungen', 'Personaldienstleistungen', 'Pharmazeutika', 'Sport', 'Telekommunikation', 'Transport und Logistik', 'Unterhaltung', 'Versicherungen', 'Wirtschaftsprüfung, Steuern und Recht', 'Sonstige Branchen'
    c) Ensure that the industry extracted is ONLY if user explicitly mention it. The language of the industry is {LANG}.
    d) If the user input does not directly match one of the options, infer the closest industry based on the provided industry.
 
18. Seniority Level:
    a) If mentioned, extract the seniority level (e.g., 'senior', 'junior', 'medior').
    b) Format as a string.
 
OUTPUT STRUCTURE:
Ensure the output is structured as follows.
Each output must start with "{" and end with "}".
Do not include any other information or format the output as a JSON object.
 
{
    "jobTitle": [],
    "city": "",
    "country": "",
    "radius": 0,
    "mandatorySkills": [],
    "optionalSkills": [],
    "mandatoryLanguages": [],
    "optionalLanguages": [],
    "yearsOfExperienceFrom": 0,
    "yearsOfExperienceTo": 0,
    "yearsInJobFrom": 0,
    "yearsInJobTo": 0,
    "email": false,
    "phone": false,
    "worksAt": [],
    "doesNotWorkAt": [],
    "previouslyWorkedAt": [],
    "doesNotPreviouslyWorkAt": [],
    "personIs": [],
    "personIsNot": [],
    "previouslyAs": "",
    "doesNotPreviouslyWorkAs": "",
    "industry": "",
    "level": ""
}
 
Make sure to adhere strictly to this format to avoid any errors.
"""





system_instruction_suggestion = """
You are an assistant tasked with extracting specific information from user inputs where applicable. Follow these instructions carefully to extract and structure the required details.
 
Extraction Requirements:
1. Job Title:
    a) Extract the job titles mentioned in the user input.
    b) Exclude any gender-related terms (e.g., m/f/d, w/m/d).
    c) Format as a list.
    d) Ensure the job titles are in the original language and if exist variation on gender in german language, add it (e.g., 'Software Engineer' then add 'Software Engineerin' as well). ALWAYS ADD THE GENDER VARIATION IN GERMAN LANGUAGE!
    e) When dealing with German job titles, always include gender variations. For example, if a job title is "Software Engineer," add "Software Engineerin" as well. Ensure this gender normalization is only applied to German job titles and not to English titles that do not require it (e.g., "Sales Representative" should not be altered).
    
 
2. City:
    a) Extract the city related to the job position.
    b) Maintain the original language (fix typos if necessary).
    c) Do not translate the city name.
 
3. Country:
    a) Extract the country related to the job position.
    b) Maintain the original language (fix typos if necessary).
    c) Do not translate the country name.
 
4. Radius:
    a) Extract the distance to the location specified.
    b) Format as a numerical value.
 
5. Mandatory Skills:
    a) Extract key skills required for the role.
    b) Provide shorter versions of the skills (e.g., 'python' instead of 'Python programming language').
 
6. Optional Skills:
    a) Extract desirable skills that are beneficial for the role.
    b) Provide shorter versions of the skills (e.g., 'python' instead of 'Python programming language').
    c) Educational level if mentioned add as skill (e.g., 'Master's degree' then add 'Master's degree' as well)
    d) For educational level add if makes sense the field of study (e.g., 'Master's degree in Computer Science' then add 'Computer Science' as well)
 
7. Languages Required:
    a) Extract the languages required for the role.
    b) Format as two lists (mandatory and optional languages).
 
8. Years of Experience Required:
    a) Extract the required years of experience.
    b) Specify as a range (from minimum to maximum).
 
9. Years in Job:
    a) Extract the number of years the person should have been in the current job position.
    b) Specify as a range (from minimum to maximum).
 
10. Email:
    a) Indicate whether an email address is required in the applicant's profile.
    b) Format as a boolean (true or false).
 
11. Phone:
    a) Indicate whether a phone number is required in the applicant's profile.
    b) Format as a boolean (true or false).
 
12. Company Preferences:
    a) Extract preferences for company names. Categories:
        - worksAt: List of preferred companies.
        - doesNotWorkAt: List of companies to avoid.
        - previouslyWorkedAt: List of companies the applicant has worked at before.
        - doesNotPreviouslyWorkAt: List of companies the applicant should not have worked at before.
    b) Exclude industry mentions.
    c) Exclude words startup, start-up and 'start up' as it is not considered as a company name. (e.g. previously worked at a startup should not be considered as a company name)
    d) DO NOT ADD STARTUP, START UP, START-UP AS A COMPANY NAME!
 
13. Person Is:
    a) From the job description, identify if any of the following descriptors are explicitly mentioned: 'Consultant', 'Executive', 'Freelancer', 'Scientist', 'Student'.
    b) If a descriptor is mentioned, include it in the personIs list.
    c) Format the extracted descriptors as a list.
    d) If the user is looking for data scientist, do not add 'Scientist' as a personIs descriptor.
 
14. Person Is Not:
    a) Extract descriptors the person should not be (e.g., 'Consultant', 'Executive', 'Freelancer', 'Scientist', 'Student').
    b) Format as a list based on user input.
 
15. Previously As:
    a) Extract the previous job title if mentioned.
    b) Format as a string.
 
16. Does Not Previously Work As:
    a) Specify the job title the person should not have previously worked as.
    b) Format as a string.
 
17. Industry:
    a) Extract the sector or field of the job position. The only options are: 'Agriculture', 'Architecture and Planning', 'Arts and Culture', 'Audit, Tax and Legal', 'Automotive', 'Aviation and Aerospace', 'Banks and Financial Services', 'Chemicals', 'Construction', 'Consultancy', 'Consumer Goods and Retail', 'Education, Training and Science', 'Energy, Water and Environment', 'Entertainment', 'Gambling and Casinos', 'Health and Wellness', 'HR Services', 'Industrial and Mechanical Engineering', 'Insurance', 'IT and Internet', 'Leisure, Tourism and Gastronomy', 'Marketing, PR and Design', 'Media and Publishing', 'Pharmaceuticals', 'Public Service, Federations and Institutions', 'Real Estate', 'Sport', 'Telecommunication', 'Transport and Logistics', 'Other Sectors'
    b) German names of the industries are also allowed and here is their list: 'Architektur und Planung', 'Automobil', 'Banken und Finanzdienstleistungen', 'Beratung und Consulting', 'Chemieindustrie', 'Energie, Wasser und Umwelt', 'Erziehung, Bildung und Wissenschaft', 'Freizeit, Tourismus und Gastronomie', 'Gambling and Casinos', 'Gesundheit und Wellness', 'Immobilien', 'Industrie und Maschinenbau', 'Internet und Informationstechnologie', 'Konstruktion', 'Konsumgüter und Handel', 'Kunst und Kultur', 'Landwirtschaft', 'Luft- und Raumfahrt', 'Marketing, PR und Design', 'Medien und Verlage', 'Öffentlicher Dienst, Verbände und Einrichtungen', 'Personaldienstleistungen', 'Pharmazeutika', 'Sport', 'Telekommunikation', 'Transport und Logistik', 'Unterhaltung', 'Versicherungen', 'Wirtschaftsprüfung, Steuern und Recht', 'Sonstige Branchen'
    c) Ensure that the industry extracted is ONLY if user explicitly mention it. The language of the industry is {LANG}.
    d) If the user input does not directly match one of the options, infer the closest industry based on the provided industry.
 
18. Seniority Level:
    a) If mentioned, extract the seniority level (e.g., 'senior', 'junior', 'medior').
    b) Format as a string.
    
19. Job Title Suggestions:
    a) If job title is provided, suggest 2-3 more similar job title options.
    b) IMPORTANT: IF JOB TITLE IS PROVIDED, YOU MUST ALWAYS SUGGEST 2-3 MORE SIMILAR JOB TITLE OPTIONS. ALSO, FOR THOSE SUGGESTIONS YOU MUST DO GERMAN GENDER VARIANT IF IT EXISTS (DESCRIBED ABOVE)!
    Example: (I am looking for a Data scitentist) -> jobTitleSuggestions: ['AI Scientist', 'AI Scientistin', 'Data Engineer', 'Data Engineerin']
    
20. Skills Suggestions:
    a) If job title is provided, suggest 2-6 skills based on job title.
    b) If job title and skills are suggested, provide more skills suggestions.
    c) If only skills are provided, suggest 6-7 skills based on the skills provided.
    d) If there are already large number of skills there is no need to suggest more skills.
    e) Provide 2-6 skills suggestions. If already exists large number of skills, add just 2-3 and if there is small number of skills, expand them with 6-7 skills, and so on.
    f) YOU MUST ALWAYS SUGGEST 2-6 SKILLS BUT ONLY IF THERE IS NOT ALREADY LARGE NUMBER OF SKILLS PROVIDED! IF THERE IS NO SKILLS AT ALL PROVIDED, YOU MUST SUGGEST 6-7 SKILLS BASED ON JOB TITLE! 
    
 
OUTPUT STRUCTURE:
Ensure the output is structured as follows.
Each output must start with "{" and end with "}".
Do not include any other information or format the output as a JSON object.
 
{
    "jobTitle": [],
    "city": "",
    "country": "",
    "radius": 0,
    "mandatorySkills": [],
    "optionalSkills": [],
    "mandatoryLanguages": [],
    "optionalLanguages": [],
    "yearsOfExperienceFrom": 0,
    "yearsOfExperienceTo": 0,
    "yearsInJobFrom": 0,
    "yearsInJobTo": 0,
    "email": false,
    "phone": false,
    "worksAt": [],
    "doesNotWorkAt": [],
    "previouslyWorkedAt": [],
    "doesNotPreviouslyWorkAt": [],
    "personIs": [],
    "personIsNot": [],
    "previouslyAs": "",
    "doesNotPreviouslyWorkAs": "",
    "industry": "",
    "level": "",
    "jobTitleSuggestions": [],
    "skillsSuggestions": []
}
 
Make sure to adhere strictly to this format to avoid any errors.
"""
# Placeholder for a real authentication mechanism
def check_credentials(username, password):
    # Fetch the password from environment variables
    correct_password = os.getenv('USER_PASSWORD')
    return username == "talentwunder" and password == correct_password
 
 
# Function to display the login form
def display_login_form():
    st.title("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        if login_button:
            if check_credentials(username, password):
                st.session_state['logged_in'] = True
                st.success("Logged in successfully.")
                # Using st.experimental_rerun() to force the app to rerun might help, but use it judiciously.
                st.rerun()
            else:
                st.error("Incorrect username or password.")
                
def data_extraction(job_description, lang_option, suggestions=False):
    
    if suggestions == True:
        instruction = system_instruction_suggestion
    else:
        instruction = system_instruction
        
    instruction = instruction.replace("{LANG}", lang_option)
        
    completion = client.chat.completions.create(
                  model='gpt-4o',
                  temperature=0,
                  top_p=0,
                  messages=[
                    {"role": "system", "content": instruction},
                    {"role": "user", "content": job_description},
                ])
    
    generated_text = completion.choices[0].message.content  
    # print(generated_text)
    try:
        parsed_output = parse_gpt_output(generated_text)
        return parsed_output
    except Exception as e:
        print(f"Error in parsing the GPT output: {e}")
        st.error(parsed_output)
        # return GptOutput()
    
def denormalize_job_title(s):
    pattern = r'\b(\S*/in)\b'

    matches = re.findall(pattern, s)

    if matches:
        if ' ' in s.strip():
            without_in = re.sub(pattern, lambda m: m.group(1)[:-3], s)  # Remove /in
            with_in = re.sub(pattern, lambda m: m.group(1)[:-3] + 'in', s)  # Replace /in with in
            return [without_in, with_in]
        else:
            return [re.sub(pattern, lambda m: m.group(1)[:-3] + '*', s)]
    else:
        if ' ' in s.strip():
            return [s, s + 'in']
        else:
            return [s + '*']
    
    
def query_title(job_title, lang, suggestions):
    
    if lang == 'de':
        job_titles = []
        for job in job_title:
            job_titles.extend(denormalize_job_title(job))
        job_titles = list(set(job_titles))
    else:
        job_titles = list(set(job_title))
    
    job_query = ' OR '.join([job if ' ' not in job else f'"{job}"' for job in job_titles])
    
    return f'({job_query})'


def query_title_v2(job_title, lang, suggestions):
    
    job_titles = list(set(job_title))
    job_query = ' OR '.join([job if ' ' not in job else f'"{job}"' for job in job_titles])
    
    return f'({job_query})'


def query_location(city=None, country=None, distance=0):
    location = ''
    
    if city:
        location += f'{city}'
    
    if location and distance > 0:
        location += f' DISTANCE {distance}'
        
    return location


def query_location_v2(city=None, country=None, distance=0, lang='de'):

    location = ''
    city_normalized, country_normalized = get_city_country(url="https://photon.komoot.io", city=city, country=country, lang=lang)
    if city_normalized:
        location += f' IN {city_normalized}'
    
    if location and distance > 0:
        location += f' DISTANCE {distance}'
    elif location and distance<=0:
        location += f' DISTANCE 50'
        
    if location and country_normalized:
        if ' ' in country_normalized.strip():
            location += f' COUNTRY "{country_normalized}"'
        else:
            location += f' COUNTRY {country_normalized}'
    elif country_normalized:
        if ' ' in country_normalized.strip():
            location = f' COUNTRY "{country_normalized}"'
        else:
            location = f' COUNTRY {country_normalized}'
        
    return location


def query_languages(optional_skills=[], mandatory_skills=[]):
    skills_set = set(optional_skills + mandatory_skills)
    languages = {skill for skill in skills_set if skill.lower() in languages_all}
    return ' AND '.join([f'"{lang}"' for lang in languages])


def query_languages_v2(languages=[]):
    langs = {lang for lang in languages if lang.lower() in languages_all}
    return ' AND '.join([f'"{lang}"' for lang in langs])


def query_languages_v3(mandatory_languages=[], optional_languages=[]):
    full_query = ""
    mandatory_query = ""
    mandatory_langs, optional_langs = [], []
        
    if len(mandatory_languages) > 0:
        mandatory_langs = {lang for lang in mandatory_languages if lang.lower() in languages_all}
        mandatory_query = ' AND '.join([f'"{lang}"' for lang in mandatory_langs])
    full_query += mandatory_query
    
    if len(optional_languages) > 0:
        optional_langs = {lang for lang in optional_languages if lang.lower() in languages_all}
        
        if len(mandatory_langs) > 0:
            for lang in optional_langs:
                optional_query = ' AND '.join([f'"{l}"' for l in list(mandatory_langs) + [lang] if l.lower() in languages_all])
                # optional_query = f' {mandatory_query} OR "{lang}"'
                full_query += f' OR ({optional_query})' 
        else:
            full_query += ' OR '.join([f'"{lang}"' for lang in optional_langs])
        
    return full_query
    
    
def boolean_query_v2(job_title, city, country, radius, mandatory_skills, optional_skills,
                                mandatory_languages, optional_languages, yearsOfExperienceFrom, yearsOfExperienceTo, yearsInJobFrom, yearsInJobTo,
                                email, phone, worksAt, doesNotWorkAt, previouslyWorkedAt, doesNotPreviouslyWorkAt,
                                personIs, personIsNot, doesNotPreviouslyWorkAs, previouslyAs, lang, level, industry):
    
    query = ""
    
    if job_title and len(job_title) > 0:
        query = query_title_v2(job_title=job_title, lang=lang, suggestions=False)
    location_query = query_location_v2(city, country, radius, lang)
    
    languages_query = ''
    # if languages:
    #     languages_query = query_languages_v2(languages)
    languages_query = query_languages_v3(mandatory_languages, optional_languages)
    
    # if skills_query:
    #     query += f' AND {skills_query}'
    skills = list(set(optional_skills + mandatory_skills))
    if len(skills) > 0:
        optional_query = ' OR '.join([f'"{skill}"' for skill in skills if skill.lower() not in languages_all and skill!=''])
        if query:
            query += f' AND ({optional_query})'
        else:
            query += f'({optional_query})'

    if location_query:
        query += f' {location_query}'
        
    if languages_query:
        query += f' SPEAKS {languages_query}'
        
    if previouslyAs:
        query += f' PREVIOUSLY_AS "{previouslyAs}"'
        
    if doesNotPreviouslyWorkAs:
        query += f' PREVIOUSLY_AS NOT "{doesNotPreviouslyWorkAs}"'
        
    if worksAt:
        worksAtQuery = ' OR '.join([f'"{work}"' for work in worksAt])
        query += f' AT {worksAtQuery}'
        
    if doesNotWorkAt:
        doesNotWorkAtQuery = ' OR '.join([f'"{work}"' for work in doesNotWorkAt])
        query += f' AT NOT {doesNotWorkAtQuery}'
        
    if previouslyWorkedAt:
        previouslyWorkedAtQuery = ' OR '.join([f'"{work}"' for work in previouslyWorkedAt])
        query += f' PREVIOUSLY_AT {previouslyWorkedAtQuery}'
        
    if doesNotPreviouslyWorkAt:
        doesNotPreviouslyWorkAtQuery = ' OR '.join([f'"{work}"' for work in doesNotPreviouslyWorkAt])
        query += f' PREVIOUSLY_AT NOT {doesNotPreviouslyWorkAtQuery}'
        
    predefined_elements = ['CONSULTANT', 'ENTREPRENEUR', 'FREELANCER', 'SCIENTIST', 'STUDENT']
    if len(personIs):
        queryPersonIs = ' '.join([f' IS {person.upper()}' for person in personIs if person.upper() in predefined_elements])
        query += queryPersonIs
        
    if len(personIsNot):
        queryPersonIsNot = ' '.join([f' IS NOT {person.upper()}' for person in personIsNot if person.upper() in predefined_elements])
        query += queryPersonIsNot
        
    if (yearsOfExperienceFrom>0) or (yearsOfExperienceTo>0):
        if ((yearsOfExperienceTo == 0) or (yearsOfExperienceTo <= yearsOfExperienceFrom)):
            yearsOfExperienceTo = yearsOfExperienceFrom+10
        query += f' YEARS_WORKING {yearsOfExperienceFrom} TO {yearsOfExperienceTo}'
        
    if (yearsInJobFrom>0) or (yearsInJobTo>0):
        if ((yearsInJobTo == 0) or (yearsInJobTo <= yearsInJobFrom)):
            yearsInJobTo = yearsInJobFrom+10
        query += f' YEARS_IN_JOB {yearsInJobFrom} TO {yearsInJobTo}' 
        
    if email:
        query += f' HAS EMAIL'
        
    if phone:
        query += f' HAS PHONE'
        
    if level and (level.lower() != 'senior'):
        query += f' AS {level}'
    
    INDUSTRIES_EN = ['Agriculture', 'Architecture and Planning', 'Arts and Culture', 'Audit, Tax and Legal', 'Automotive', 'Aviation and Aerospace', 'Banks and Financial Services', 'Chemicals', 'Construction', 'Consultancy', 'Consumer Goods and Retail', 'Education, Training and Science', 'Energy, Water and Environment', 'Entertainment', 'Gambling and Casinos', 'Health and Wellness', 'HR Services', 'Industrial and Mechanical Engineering', 'Insurance', 'IT and Internet', 'Leisure, Tourism and Gastronomy', 'Marketing, PR and Design', 'Media and Publishing', 'Pharmaceuticals', 'Public Service, Federations and Institutions', 'Real Estate', 'Sport', 'Telecommunication', 'Transport and Logistics', 'Other Sectors']  
    INDUSTRIES_DE = {'Architektur und Planung': 'Architecture and Planning', 'Automobil': 'Automotive', 'Banken und Finanzdienstleistungen': 'Banks and Financial Services', 'Beratung und Consulting': 'Consultancy', 'Chemieindustrie': 'Chemicals', 'Energie, Wasser und Umwelt': 'Energy, Water and Environment', 'Erziehung, Bildung und Wissenschaft': 'Education, Training and Science', 'Freizeit, Tourismus und Gastronomie': 'Leisure, Tourism and Gastronomy', 'Gambling and Casinos': 'Gambling and Casinos', 'Gesundheit und Wellness': 'Health and Wellness', 'Immobilien': 'Real Estate', 'Industrie und Maschinenbau': 'Industrial and Mechanical Engineering', 'Internet und Informationstechnologie': 'IT and Internet', 'Konstruktion': 'Construction', 'Konsumgüter und Handel': 'Consumer Goods and Retail', 'Kunst und Kultur': 'Arts and Culture', 'Landwirtschaft': 'Agriculture', 'Luft- und Raumfahrt': 'Aviation and Aerospace', 'Marketing, PR und Design': 'Marketing, PR and Design', 'Medien und Verlage': 'Media and Publishing', 'Öffentlicher Dienst, Verbände und Einrichtungen': 'Public Service, Federations and Institutions', 'Personaldienstleistungen': 'HR Services', 'Pharmazeutika': 'Pharmaceuticals', 'Sport': 'Sport', 'Telekommunikation': 'Telecommunication', 'Transport und Logistik': 'Transport and Logistics', 'Unterhaltung': 'Entertainment', 'Versicherungen': 'Insurance', 'Wirtschaftsprüfung, Steuern und Recht': 'Audit, Tax and Legal', 'Sonstige Branchen': 'Other Sectors'}
    if industry:
        if lang == 'de':
            if industry in INDUSTRIES_DE.keys():
                query += f' INDUSTRY "{INDUSTRIES_DE[industry]}"'
            else:
                query += f' INDUSTRY "Other Sectors"'
        else:
            if industry in INDUSTRIES_EN:
                query += f' INDUSTRY "{industry}"'
            else:
                query += f' INDUSTRY "Other Sectors"'
            
    return query
                
                
def display_main_app():
    st.title('AI Search Generator')
    selected_model = "gpt-4o"
    lang_option = st.selectbox(
    "Application language:",
    ("de", "en"))
    # suggestion = st.selectbox(
    # "Job titles expansion (AI suggesting):",
    # ("True", "False"))
    wav_audio_data = st_audiorec()
    # user_input = st.text_area("Enter your prompt:", height=50)
 
    if wav_audio_data is not None:
        start_time = time.time()
        audio_file = BytesIO(wav_audio_data)
        audio_file.name = "audio.wav" 

        user_input = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            response_format="text",
            language=lang_option)
        
        if user_input:
            st.write(user_input)
            with st.spinner('Generating text... Please wait'):
                # gpt_output = data_extraction(user_input, lang_option, False)
                gpt_output_suggestion = data_extraction(user_input, lang_option, True)
                # job_title_suggestion = gpt_output_suggestion.model_dump().get("jobTitle")
                # mandatory_skills_suggestion = gpt_output_suggestion.model_dump().get("mandatorySkills")
                # optional_skills_suggestion = gpt_output_suggestion.model_dump().get("optionalSkills")
                job_title = gpt_output_suggestion.model_dump().get("jobTitle")
                city = gpt_output_suggestion.model_dump().get("city")
                country = gpt_output_suggestion.model_dump().get("country")
                radius = gpt_output_suggestion.model_dump().get("radius")
                mandatory_skills = gpt_output_suggestion.model_dump().get("mandatorySkills")
                optional_skills = gpt_output_suggestion.model_dump().get("optionalSkills")
                mandatory_languages = gpt_output_suggestion.model_dump().get("mandatoryLanguages")
                optional_languages = gpt_output_suggestion.model_dump().get("optionalLanguages")
                yearsOfExperienceFrom = gpt_output_suggestion.model_dump().get("yearsOfExperienceFrom")
                yearsOfExperienceTo = gpt_output_suggestion.model_dump().get("yearsOfExperienceTo")
                yearsInJobFrom = gpt_output_suggestion.model_dump().get("yearsInJobFrom")
                yearsInJobTo = gpt_output_suggestion.model_dump().get("yearsInJobTo")
                email = gpt_output_suggestion.model_dump().get("email")
                phone = gpt_output_suggestion.model_dump().get("phone")
                worksAt = gpt_output_suggestion.model_dump().get("worksAt")
                doesNotWorkAt = gpt_output_suggestion.model_dump().get("doesNotWorkAt")
                previouslyWorkedAt = gpt_output_suggestion.model_dump().get("previouslyWorkedAt")
                doesNotPreviouslyWorkAt = gpt_output_suggestion.model_dump().get("doesNotPreviouslyWorkAt")
                personIs = gpt_output_suggestion.model_dump().get("personIs")
                personIsNot = gpt_output_suggestion.model_dump().get("personIsNot")
                previouslyWorkedAt = gpt_output_suggestion.model_dump().get("previouslyWorkedAt")
                doesNotPreviouslyWorkAs = gpt_output_suggestion.model_dump().get("doesNotPreviouslyWorkAs")
                personIs = gpt_output_suggestion.model_dump().get("personIs")
                personIsNot = gpt_output_suggestion.model_dump().get("personIsNot")
                previouslyAs = gpt_output_suggestion.model_dump().get("previouslyAs")
                doesNotPreviouslyWorkAs = gpt_output_suggestion.model_dump().get("doesNotPreviouslyWorkAs")
                level = gpt_output_suggestion.model_dump().get("level")
                industry = gpt_output_suggestion.model_dump().get("industry")
                job_title_suggestion = gpt_output_suggestion.model_dump().get("jobTitleSuggestions")
                skills_suggestion = gpt_output_suggestion.model_dump().get("skillsSuggestions")
        
                result = boolean_query_v2(job_title, city, country, radius, mandatory_skills, optional_skills,
                                        mandatory_languages, optional_languages, yearsOfExperienceFrom, yearsOfExperienceTo, yearsInJobFrom, yearsInJobTo,
                                        email, phone, worksAt, doesNotWorkAt, previouslyWorkedAt, doesNotPreviouslyWorkAt,
                                        personIs, personIsNot, doesNotPreviouslyWorkAs, previouslyAs, lang_option, level, industry)

                job_title_v2 = list(set(job_title + job_title_suggestion))
                optional_skills_suggestion = list(set(optional_skills + skills_suggestion))
                result_ai = boolean_query_v2(job_title_v2, city, country, radius, mandatory_skills, optional_skills_suggestion,
                                        mandatory_languages, optional_languages, yearsOfExperienceFrom, yearsOfExperienceTo, yearsInJobFrom, yearsInJobTo,
                                        email, phone, worksAt, doesNotWorkAt, previouslyWorkedAt, doesNotPreviouslyWorkAt,
                                        personIs, personIsNot, doesNotPreviouslyWorkAs, previouslyAs, lang_option, level, industry)
                
                st.markdown("### Raw query")
                st.markdown(result)
                st.markdown("### Query with AI suggestions")
                st.markdown(result_ai)
                end_time = time.time()
                st.write(f"Time taken: {end_time - start_time:.2f} seconds")
                
 
# Decide which part of the app to display based on login status
if not st.session_state['logged_in']:
    display_login_form()
else:
    display_main_app()