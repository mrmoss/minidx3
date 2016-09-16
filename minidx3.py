#!/usr/bin/env python
import array
import hid
import time


#NEED:
#  P (Set Pin)
#  B (Get Reg)
#  C (Set Reg)
#  S (Set Date)
#  All helpers for registers

def crc(data):
	crc=0
	for ii in range(len(data)):
		crc^=data[ii]
	return crc

def array_to_str(arr):
	text=""
	for ii in range(len(arr)):
		text+=chr(arr[ii])
	return text

def str_to_array(text):
	return [ord(ii) for ii in text]

def pack(payload):
	if type(payload) is str:
		payload=str_to_array(payload)
	size=[len(payload)&0xff00,len(payload)&0x00ff]
	return [0x02]+size+payload+[crc(size+payload)]

def send_packet(dev,payload):
	dev.send_feature_report(pack(payload))

def recv_packet(dev):
	data=dev.read(256)
	min_size=4
	if len(data)<min_size:
		raise Exception("Packet too small (is "+str(len(data))+" but min size is "+str(min_size)+").")
	header=data[0]
	if header!=0x02:
		raise Exception("Invalid header (got "+str(hex(header))+" expected 0x02).")
	size=(data[1]<<8)+data[2]
	while True:
		max_size=len(data)-min_size
		if size<=max_size:
			break
		data+=dev.read(256)
	payload=data[3:3+size]
	checksum=data[3+size]
	checksum_calc=pack(payload)[-1]
	if pack(payload)[-1]!=checksum:
		raise Exception("Invalid checksum (got "+str(hex(checksum))+" expected "+str(hex(checksum_calc))+").")
	return payload

def parse_date(buf):
	if len(buf)!=15:
		raise Exception("Expected a date string size of 15 bytes got "+str(date_size)+" bytes.")

	date={}
	date['year']=array_to_str(buf[:4])
	date['month']=array_to_str(buf[4:6])
	date['day']=array_to_str(buf[6:8])
	date['hour']=array_to_str(buf[8:10])
	date['minute']=array_to_str(buf[10:12])
	date['second']=array_to_str(buf[12:15])

	return date

def login(dev,pin):
	ptype='L'
	send_packet(dev,ptype+pin)
	buf=recv_packet(dev)

	if len(buf)<2:
		raise Exception("Invalid response size (expected at least 2 bytes got "+str(len(buf))+" bytes).")

	rtype=chr(buf[0])
	buf=buf[1:]
	if rtype!=ptype:
		raise Exception("Invalid response type (expected '"+ptype+"' got '"+rtype+"').")

	code=chr(buf[0])
	buf=buf[1:]
	if code!='0' and code!='1':
		raise Exception("Received error code ("+code+").")

	return code is '0'

def logout(dev):
	ptype='O'
	send_packet(dev,ptype)
	buf=recv_packet(dev)

	if len(buf)<2:
		raise Exception("Invalid response size (expected at least 2 bytes got "+str(len(buf))+" bytes).")

	rtype=chr(buf[0])
	buf=buf[1:]
	if rtype!=ptype:
		raise Exception("Invalid response type (expected '"+ptype+"' got '"+rtype+"').")

	code=chr(buf[0])
	buf=buf[1:]
	if code!='0' and code!='1':
		raise Exception("Received error code ("+code+").")


def get_num(dev):
	ptype='N'
	send_packet(dev,ptype)
	buf=recv_packet(dev)

	if len(buf)<2:
		raise Exception("Invalid response size (expected at least 2 bytes got "+str(len(buf))+" bytes).")

	rtype=chr(buf[0])
	buf=buf[1:]
	if rtype!=ptype:
		raise Exception("Invalid response type (expected '"+ptype+"' got '"+rtype+"').")

	code=chr(buf[0])
	buf=buf[1:]
	if code!='0':
		raise Exception("Received error code ("+code+").")

	if len(buf)!=2:
		raise Exception("Malformed packet (expected 2 bytes got "+len(buf)+" bytes).")

	return (buf[0]<<8)+buf[1]

def mprint(arr):
	print(array_to_str(arr)+" - "+str(arr))

def get_entry(dev,index):
	ptype='G'
	send_packet(dev,ptype+chr((index&0xff00)>>8)+chr(index&0x00ff))
	buf=recv_packet(dev)

	if len(buf)<2:
		raise Exception("Invalid response size (expected at least 2 bytes got "+str(len(buf))+" bytes).")

	rtype=chr(buf[0])
	buf=buf[1:]
	if rtype!=ptype:
		raise Exception("Invalid response type (expected '"+ptype+"' got '"+rtype+"').")

	code=chr(buf[0])
	buf=buf[1:]
	if code!='0':
		raise Exception("Received error code ("+code+").")

	if len(buf)<1:
		raise Exception("Malformed packet (expected at least 1 byte got 0 bytes).")

	date_size=buf[0]
	buf=buf[1:]

	if len(buf)<date_size:
		raise Exception("Malformed packet (expected at least "+str(date_size)+" bytes got "+str(len(buf))+" bytes).")
	date=buf[:date_size]
	buf=buf[date_size:]

	if len(buf)<3:
		raise Exception("Malformed packet (expected at least 3 bytes got "+str(len(buf))+" bytes).")
	track_sizes=buf[:3]
	buf=buf[3:]

	tracks=[]
	for ii in range(3):
		track_size=track_sizes[ii]
		if len(buf)<track_size:
			raise Exception("Malformed packet (expected at least "+str(track_size)+" bytes got "+str(len(buf))+" bytes).")
		track=array_to_str(buf[:track_size])
		buf=buf[track_size:]
		tracks.append(track)

	date=parse_date(date)

	return tracks

def erase(dev):
	ptype='E'
	send_packet(dev,ptype)
	buf=recv_packet(dev)

	if len(buf)<2:
		raise Exception("Invalid response size (expected at least 2 bytes got "+str(len(buf))+" bytes).")

	rtype=chr(buf[0])
	buf=buf[1:]
	if rtype!=ptype:
		raise Exception("Invalid response type (expected '"+ptype+"' got '"+rtype+"').")

	code=chr(buf[0])
	buf=buf[1:]
	if code!='0':
		raise Exception("Received error code ("+code+").")

def get_date(dev):
	ptype='T'
	send_packet(dev,ptype)
	buf=recv_packet(dev)

	if len(buf)<2:
		raise Exception("Invalid response size (expected at least 2 bytes got "+str(len(buf))+" bytes).")

	rtype=chr(buf[0])
	buf=buf[1:]
	if rtype!=ptype:
		raise Exception("Invalid response type (expected '"+ptype+"' got '"+rtype+"').")

	code=chr(buf[0])
	buf=buf[1:]
	if code!='0':
		raise Exception("Received error code ("+code+").")

	return parse_date(buf)

def get_product_version(dev):
	ptype='F'
	send_packet(dev,ptype)
	buf=recv_packet(dev)

	if len(buf)<2:
		raise Exception("Invalid response size (expected at least 2 bytes got "+str(len(buf))+" bytes).")

	rtype=chr(buf[0])
	buf=buf[1:]
	if rtype!=ptype:
		raise Exception("Invalid response type (expected '"+ptype+"' got '"+rtype+"').")

	buf=array_to_str(buf)
	while len(buf)>0:
		nullbyte_index=buf.find('\0')
		if nullbyte_index<0:
			break
		buf=buf[:nullbyte_index]+buf[nullbyte_index+1:]

	return buf

def get_register(dev,register):
	ptype='B'
	send_packet(dev,ptype+register)
	buf=recv_packet(dev)
	print(buf.index(0))

if __name__=="__main__":
	h=hid.device()
	h.open(0x0801,0x0083)
	print('opened')

	if not login(h,"0000"):
		print('Failed to login.')
		exit(1)
	else:
		print('Login successful')

	get_register(h,'a')
	exit(0)

	entry_count=get_num(h)
	print("Entry count: "+str(entry_count))

	for ii in range(entry_count):
		print(get_entry(h,ii))

	h.close()