#!/usr/bin/env python
import array
import hid
import time

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

def login(dev,pin):
	ptype='L'
	send_packet(dev,ptype+pin)
	res=recv_packet(dev)

	if len(res)<2:
		raise Exception("Invalid response size (expected at least 2 bytes got "+str(len(res))+" bytes).")

	rtype=chr(res[0])
	res=res[1:]
	if rtype!=ptype:
		raise Exception("Invalid response type (expected '"+ptype+"' got '"+rtype+"').")

	code=chr(res[0])
	res=res[1:]
	if code!='0' and code!='1':
		raise Exception("Received error code ("+code+").")

	return code is '0'


def get_num(dev):
	ptype='N'
	send_packet(dev,ptype)
	res=recv_packet(dev)

	if len(res)<2:
		raise Exception("Invalid response size (expected at least 2 bytes got "+str(len(res))+" bytes).")

	rtype=chr(res[0])
	res=res[1:]
	if rtype!=ptype:
		raise Exception("Invalid response type (expected '"+ptype+"' got '"+rtype+"').")

	code=chr(res[0])
	res=res[1:]
	if code!='0':
		raise Exception("Received error code ("+code+").")

	if len(res)!=2:
		raise Exception("Malformed packet (expected 2 bytes got "+len(res)+" bytes).")

	return (res[0]<<8)+res[1]

def mprint(arr):
	print(array_to_str(arr)+" - "+str(arr))

def get_entry(dev,index):
	ptype='G'
	send_packet(dev,ptype+chr((index&0xff00)>>8)+chr(index&0x00ff))
	res=recv_packet(dev)

	if len(res)<2:
		raise Exception("Invalid response size (expected at least 2 bytes got "+str(len(res))+" bytes).")

	rtype=chr(res[0])
	res=res[1:]
	if rtype!=ptype:
		raise Exception("Invalid response type (expected '"+ptype+"' got '"+rtype+"').")

	code=chr(res[0])
	res=res[1:]
	if code!='0':
		raise Exception("Received error code ("+code+").")

	if len(res)<1:
		raise Exception("Malformed packet (expected at least 1 byte got 0 bytes).")

	date_size=res[0]
	res=res[1:]

	if len(res)<date_size:
		raise Exception("Malformed packet (expected at least "+str(date_size)+" bytes got "+str(len(res))+" bytes).")
	date=res[:date_size]
	res=res[date_size:]

	if len(res)<3:
		raise Exception("Malformed packet (expected at least 3 bytes got "+str(len(res))+" bytes).")
	track_sizes=res[:3]
	res=res[3:]

	tracks=[]
	for ii in range(3):
		track_size=track_sizes[ii]
		if len(res)<track_size:
			raise Exception("Malformed packet (expected at least "+str(track_size)+" bytes got "+str(len(res))+" bytes).")
		track=array_to_str(res[:track_size])
		res=res[track_size:]
		tracks.append(track)

	year=date[:4]
	date=date[4:]
	month=date[:2]
	date=date[2:]
	day=date[:2]
	date=date[2:]
	hour=date[:2]
	date=date[2:]
	minute=date[:2]
	date=date[2:]
	second=date[:3]
	date=date[3:]

	return tracks

if __name__=="__main__":
	h=hid.device()
	h.open(0x0801,0x0083)
	print('opened')

	if not login(h,"0000"):
		print('Failed to login.')
		exit(1)
	else:
		print('Login successful')

	entry_count=get_num(h)
	print("Entry count: "+str(entry_count))

	for ii in range(entry_count):
		print(get_entry(h,ii))

	h.close()