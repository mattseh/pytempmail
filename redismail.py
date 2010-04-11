import redis,smtpd,asyncore
class RedisMail(smtpd.SMTPServer):
	def __init__(self,host='localhost',port=8025,rhost='localhost',rport=6379,expiry=60):
		smtpd.SMTPServer.__init__(self,(host,port),None)
		self.expiry = expiry
		self.r = redis.Redis(rhost,rport)
		
	def process_message(self,peer,mailfrom,rcpttos,data):
		print 'msg from %s' % mailfrom
		recipient = rcpttos[0].split('@')[0].strip()
		mails = self.r.lrange(recipient,0,-1)
		if mails == None:
			mails = [data]
		else:
			mails = [data] + mails
		self.r.delete(recipient)
		for mail in mails:
			self.r.lpush(recipient,mail)
		self.r.ltrim(recipient,0,100)
		self.r.expire(recipient,self.expiry)
		
if __name__ == '__main__':
	rm = RedisMail()
	asyncore.loop()
