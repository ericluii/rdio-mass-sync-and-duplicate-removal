import sys

from urllib2 import HTTPError

from rdio import Rdio
from rdio_consumer_credentials import *


rdio = Rdio((RDIO_CONSUMER_KEY, RDIO_CONSUMER_SECRET))
song_data = {}

try:
  # authenticate against the Rdio service
  url = rdio.begin_authentication('oob')
  print "Go to: " + url
  verifier = raw_input("Then enter the code: ").strip()
  rdio.complete_authentication(verifier)

  print "\nFinding Duplicate Songs..."

  # get songs in collection
  songs = rdio.call('getTracksInCollection', {'sort': 'artist'})
  if (songs['status'] == 'ok'):

		# mape all songs by song name - artist
		for song in songs['result']:
			uuid = song['name'] + ' - ' + song['artist']
			data = {'name': song['name'], 'artist': song['artist'], 'album': song    ['album'], 'key': song['key'], 'url': song['shortUrl']}

			if uuid in song_data:
				song_data[uuid].append(data)
			else:
				song_data[uuid] = [data]
  else:
    print "ERROR: " + songs['message']

  print "\nList of Duplicate Songs Found:"
  print "=============================="
	# find all songs with multiple items mapped to same key
  duplicate_count = 0
  duplicate_songs = {} 
  for key in song_data:
		if len(song_data[key]) > 1:
			duplicate_count += len(song_data[key])
			duplicate_songs[key] = song_data[key]
			print key

  print "=============================="
  print "Total Duplicates Found: " + str(duplicate_count) + " songs\n"

  raw_input("Press enter to continue")

	# iterate through songs and try to delete duplicates
  songs_to_delete = []
  songs_to_keep = []
  keys = []
  for key in duplicate_songs:
		print "\nDuplicate Song: " + key
		i = 1
		# display ll the duplicates of a certain track
		for song in duplicate_songs[key]:
			print "  " + str(i) + ". " + key + "(" + song['album'] + ") -- " + song['url']
			i += 1

		j = 1
		# ask to delete each song
		while len(duplicate_songs[key]) > 0:
			shouldDelete = raw_input("Remove " + str(j) + ". " + key + "(" + duplicate_songs[key][0]['album'] + ")?[y/n] ").strip()
			if shouldDelete == 'y':
				songs_to_delete.append(duplicate_songs[key][0])
				keys.append(duplicate_songs[key][0]['key'])
				duplicate_songs[key].pop(0)
				j += 1
			elif shouldDelete == 'n':
				songs_to_keep.append(duplicate_songs[key][0])
				duplicate_songs[key].pop(0)
				j += 1
			elif shouldDelete == 'q':
				print "Quitting Script."
				sys.exit(0)

  print "\nSongs that you are keeping: " + str(len(songs_to_keep)) + " songs"
  print "=========================================="
  for song in songs_to_keep:
  	print song['name'] + " - " + song['artist'] + "(" + song['album'] + ") -- " + song['url']

  print "\nSongs that you are removing: " + str(len(songs_to_delete)) + " songs"
  print "=========================================="
  for song in songs_to_delete:
  	print song['name'] + " - " + song['artist'] + "(" + song['album'] + ") -- " + song['url']

  confirm_delete = False
  while not confirm_delete:
		check = raw_input("\nAre you sure this is correct?[y/n] ")
		if check == 'y':
			confirm_delete = True
		elif check == 'n':
			print "Quitting Script -- Nothing has changed."
			sys.exit(0)

  # create a comma separated string
  keys_string = ",".join(keys)
  rdio.call('removeFromCollection', {'keys': keys_string})
  print "Request sent. Open your Rdio mobile app to check your collection."

except HTTPError, e:
  # if we have a protocol error, print it
  print e.read()
