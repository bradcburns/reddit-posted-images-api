#!/usr/bin/env python

import argparse
import sys
import requests
import time

class UserNotFound(Exception):
	def __init__(self,user):
		self.user = user
	def __str__(self):
		return ('user ' + self.user + ' was not found in Reddit. ' +
			'Verify the spelling and try again.')

def WriteStringToFile(filename,string):
	with open(filename,'w') as filo:
		filo.write(string)
	return True

def get_comments(user):

	ListComments = []


	#TODO make this user-agent string session-unique.
	StrRequestHeaders = {'user-agent':'https://github.com/bradcburns/Get-Reddit-Posted-Photos/'}
	StrCommentsAPIURL = ("http://reddit.com/" +
		"user/" + user + "/comments.json")

	r = requests.get(StrCommentsAPIURL,headers=StrRequestHeaders)

	if r.status_code == 404:
		raise UserNotFound(user)

	JsonResponse = r.json()

	#Yes, Reddit calls it a "thing", the following variable name isn't just a
	#lazy naming convention on my part.

	JsonResponseNextThing = JsonResponse['data']['after']

	#While Reddit is still telling us there are more pages of comments,
	#request the next page and store it.
	while JsonResponseNextThing:
		r = requests.get(StrCommentsAPIURL,headers=StrRequestHeaders,params={'after':JsonResponseNextThing})

		JsonResponse = r.json()

		for comment in JsonResponse['data']['children']:
			ListComments.append(comment)

		JsonResponseNextThing = JsonResponse['data']['after']

	return ListComments

def GetImageURLsFromComment(comment):
	print 'scraping through comments for image links...'
	ListImageURLs = []

	StrCommentText = comment['data']['body']

	ListImageFileExtensions = ([
		'.jpg','.jpeg','.png',
		'.tif','.tiff','.gif',
		'.gifv'])

	#Instantiate a variable that we will use to store
	#the location of an image file extension if we find
	#it.
	IntExtensionIndexFound = 0
	IntHTTPIndexFound = 0

	for extension in ListImageFileExtensions:
		#find one of the extensions in the comment's body, starting with
		#where the last extension is found. first search starts at 0
		#per the variable IntExtensionIndexFound's instatiation above.
		IntExtensionIndexFound = StrCommentText.find(extension)
		while IntExtensionIndexFound > -1:
			
			#search backwards in the string from where
			#we found the file extension for the beginning
			#of a URL. if we didn't find it, then exit
			#because there won't be a useful URL. sadface.jpg
			IntHTTPIndexFound = StrCommentText.rfind('http',
				0,IntExtensionIndexFound)
			
			if IntHTTPIndexFound > -1:
				#Skip if there's a space between the http and the image extension
				#the characters in between are likely not an image link.
				IntSpaceFound = StrCommentText.find(' ',IntHTTPIndexFound,IntExtensionIndexFound)
				if IntSpaceFound > -1:
					print 'space before http found in ' + StrCommentText 
					IntExtensionIndexFound = StrCommentText.find(extension,0,IntExtensionIndexFound)
					continue
			else:
				#if there's no http found, then just search for the next image link
				IntExtensionIndexFound = StrCommentText.find(extension,0,IntExtensionIndexFound)
				continue

			#slice out the image url and store it
			StrImageURL = StrCommentText[IntHTTPIndexFound:IntExtensionIndexFound + len(extension)]
			ListImageURLs.append(StrImageURL)

			IntExtensionIndexFound = StrCommentText.find(extension,0,IntExtensionIndexFound)

	return ListImageURLs

def GetLinksInHTML(urls,args):
	StrHTMLHeader = (
		'<html>'
		'<head>'
		'<title>Reddit Image Links for {user}</title>'
		'</head>'
		'<body>'.format(user=args.user))

	StrHTMLBody = ''

	if not urls:
		StrHTMLBody = ("woah, doesn't look" 
			"like {user} posted any links.".format(user=args.user))
	else:
		for link in urls:
			StrHTMLBody += ('<img src="{imagelink}'
				'">'.format(imagelink=link))
	StrHTMLFooter = '</body></html>'

	ret = StrHTMLHeader + StrHTMLBody + StrHTMLFooter

	return ret

def verify_args(args):
	return True

def parse_args():
	
	StrProgramDescrip = ("scrape_reddit_images is a script "
		"which will return the images a reddit user has posted "
		"in both comments and submissions. It can output as an "
		"HTML page or a csv of links. Append the --help "
		"argument to see usage.\n \n"
		"scrape_reddit_images was written by Brad Burns and is "
		"released under the MIT License.\n\n"
		"https://github.com/bradcburns\n"
		"https://www.linkedin.com/in/bradleycburns\n")

	StrUsageExample = ("example:"
		"scrape_reddit_images.py -u Karmanaut "
		"--output html")

	parser = argparse.ArgumentParser(
		description=StrProgramDescrip,
		epilog=StrUsageExample)

	parser.add_argument(
		'--user',
		'-u',
		help='full name of the user whose images you want to scrape.',
		required=True)

	parser.add_argument(
		'--output',
		'-o',
		help='format in which to output images. defaults to html.',
		default='html',
		choices=['html','csv'])

	ret = parser.parse_args()

	return ret

def main():
	args = parse_args()
	if not verify_args(args):
		raise Exception('A command-line argument is missing or '
			'improperly entered. Use the --help argument and '
			'verify your usage.')

	ListComments = get_comments(args.user)

	ListImageLinks = []

	for comment in ListComments:
		links = GetImageURLsFromComment(comment)
		ListImageLinks.extend(links)

	if args.output == 'html':
		StrHTML = GetLinksInHTML(ListImageLinks,args)
		WriteStringToFile(args.user + '_' + str(time.time()) + '.html', StrHTML)
	elif args.output == 'csv':
		#Note that this doesn't properly account for commas
		#that already exist in links prior to the join.
		StrCSV = ','.join(ListImageLinks)
		WriteStringToFile(args.user + '_' + str(time.time()) + '.csv', StrCSV)



if __name__ == "__main__":
	main()