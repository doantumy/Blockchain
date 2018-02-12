
# coding: utf-8

# In[1]:


#binary and base64string encoding and decoding
import base64
# create a writable image and write the decoding result
image_result = open('image.png', 'wb')
str_result=open("str.txt",'wb')

image = open('../img/bitcoin.png', 'rb')
image_read = image.read() #open binary file in read mode
image_64_encode = base64.encodestring(image_read)#encode binary to base64string

image_64_decode = base64.decodestring(image_64_encode)#decode base64string to binary
image_result.write(image_64_decode)
str_result.write(image_64_encode)

image.close()
image_result.close()
str_result.close()

