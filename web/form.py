import unittest


class Form:

	def __init__(self):
		self.datalist=[('Request : ','')]

	def request_form(self):
		#print "Please enter the \"fecth\" command to fetch all the data :"
		try :
			#depend on system
			sys.stdin = open('/dev/tty')
		except:
			print "not from linux bash"
			pass
			#do nothing
		#ne fonctionne pas sous docker
		v_input = raw_input("\nPlease enter the \"fetch\" command to fetch all the data :\n")
	 	return v_input

if __name__ == '__main__':
 	form = Form()
	print form.request_form()
	


