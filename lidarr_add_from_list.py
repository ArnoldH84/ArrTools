import os, time, requests, logging, logging.handlers, json, sys, re, csv
from colorlog import ColoredFormatter
import configparser
from datetime import datetime

artist_added_count=0
artist_exist_count=0

# Config ###############################################################################################################

config = configparser.ConfigParser()
config.read('./config.ini')
baseurl = config['lidarr']['baseurl']
# urlbase = config['lidarr']['urlbase']
api_key = config['lidarr']['api_key']
rootfolderpath = config['lidarr']['rootfolderpath']

# Logging ##############################################################################################################

logging.getLogger().setLevel(logging.NOTSET)

formatter = ColoredFormatter(
	"%(log_color)s[%(levelname)s]%(reset)s %(white)s%(message)s",
	datefmt=None,
	reset=True,
	log_colors={
		'DEBUG':    'cyan',
		'INFO':     'green',
		'WARNING':  'yellow',
		'ERROR':    'red',
		'CRITICAL': 'red,bg_white',
	},
	secondary_log_colors={},
	style='%'
)

logger = logging.StreamHandler()
logger.setLevel(logging.INFO) # DEBUG To show all
logger.setFormatter(formatter)
logging.getLogger().addHandler(logger)
if not os.path.exists("./logs/"): os.mkdir("./logs/")
logFileName =  "./logs/lafl.log"#.format(datetime.now().strftime("%Y-%m-%d-%H.%M.%S"))
filelogger = logging.handlers.RotatingFileHandler(filename=logFileName)
filelogger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
filelogger.setFormatter(logFormatter)
logging.getLogger().addHandler(filelogger)

log = logging.getLogger("app." + __name__)

########################################################################################################################

def add_artist(artistName,foreignArtistId):
	global artist_exist_count, artist_added_count
	# log.info("Adding {} to Lidarr.".format(artistName))
	data = json.dumps({
		"artistName" : artistName ,
		"foreignArtistId" : foreignArtistId,
		"QualityProfileId" : 1,
		"MetadataProfileId" : 1,
		"Path": os.path.join(rootfolderpath,artistName) ,
		"albumFolder": True ,
		"RootFolderPath" : rootfolderpath,
		"monitored": True
		})
	url = '{}/api/v1/artist'.format(baseurl)
	headers = {"Content-type": "application/json", "X-Api-Key": "{}".format(api_key)}
	rsp = requests.post(url, headers=headers, data=data)
	if rsp.status_code == 201:
		artist_added_count +=1
		log.info("{} Added to Lidarr :)".format(artistName))
	elif rsp.status_code == 400:
		artist_exist_count +=1
		log.info("{} already Exists in Lidarr.".format(artistName))
		return
	else:
		log.error("{} Not found, Not added to Lidarr.".format(artistName))
		return

def main():
	# print('\033c')
	global artist_exist_count
	if sys.version_info[0] < 3: log.error("Must be using Python 3"); sys.exit(-1)
	if len(sys.argv)<2: log.error("No list Specified... Bye!!"); sys.exit(-1)
	if not os.path.exists(sys.argv[1]):
		log.info("{} Does Not Exist".format(sys.argv[1]));
		sys.exit(-1)

	with open(sys.argv[1]) as csvfile:
		m = csv.reader(csvfile)
		s = sorted(m, key=lambda row:(row), reverse=False)
		total_count = len(s)
		if not total_count>0:
			log.error("No Artists Found in file... Bye!!");
			sys.exit()
		log.info("Found {} Artists in {}. :)".format(total_count,sys.argv[1]))
		for row in s:
			if not (row): continue
			num_cols = len(row)
			if num_cols == 2: artist, foreignArtistId = row
			else: log.error("There was an error reading {} Details".format(title))
			try: add_artist(artist, foreignArtistId)
			except Exception as e: log.error(e); sys.exit(-1)
	log.info("Added {} of {} Artists, {} Already Exist".format(artist_added_count,total_count,artist_exist_count))

if __name__ == "__main__":
	main()