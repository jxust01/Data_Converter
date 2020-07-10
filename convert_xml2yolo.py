import json
import os
import glob
import pandas as pd
import argparse
import xml.etree.ElementTree as ET
import cv2
import numpy as np
from skimage.measure import label, regionprops
import csv

label_dir = 'labelled'
datasets = glob.glob(os.path.join(label_dir, '*'))
print(datasets)

if not os.path.exists('images'):
	os.mkdir('images')
if not os.path.exists('labels'):
	os.mkdir('labels')
classnames = ['ST','GT', 'HG', 'TC', 'Pink', 'BB','KB', 'FB', 'PF', 'CPF']

overlay_flag = False

def write_txt(file, data):
	with open(file, 'a') as f:
		writer = csv.writer(f, delimiter = ' ')
		writer.writerow(data)


for dataset in datasets:
	xml_files = glob.glob(os.path.join(dataset, 'quads_images/*.xml'))

	if True:
		for xml_file in xml_files:
			img_path = xml_file.replace('xml', 'jpg')
			mask_path = img_path.replace('quads_images', 'mask_quads')
			img = cv2.imread(img_path)
			mask = cv2.imread(mask_path, 0)
			ret, thresh = cv2.threshold(mask, 10, 255, cv2.THRESH_BINARY)
			label_img = label(thresh)
			regions = regionprops(label_img)[0]
			minr,minc,maxr,maxc = regions.bbox

			quads_images = img[minr:maxr, minc:maxc, :]
			quad_h, quad_w = quads_images.shape[0], quads_images.shape[1]

			new_name = os.path.basename(dataset) + '_' +os.path.basename(img_path)[:-3]+'png'
			print(new_name, quad_h, quad_w)
			
			tree = ET.parse(xml_file)
			root = tree.getroot()
			annotations = []
			for member in root.findall('object'):
				value = (root.find('filename').text,
						 int(root.find('size')[0].text),
						 int(root.find('size')[1].text), member[0].text,
						 int(member[4][0].text), int(member[4][1].text),
						 int(member[4][2].text), int(member[4][3].text))
				class_name = member[0].text
				class_num = classnames.index(class_name)
				x_tl, y_tl, x_br, y_br = float(member[4][0].text), float(member[4][1].text),float(member[4][2].text), float(member[4][3].text)

				coords = [x_tl-minc, y_tl-minr, x_br-minc, y_br-minr]


				if all(i<0 for i in coords):
					print(new_name)
					continue
				else:
				#qx_tl, qy_tl, qx_br, qy_br
					newcoords = []
					for i in coords:
						if i < 0:
							i = 0
						newcoords.append(i)
					print(coords, newcoords)

				x_min = newcoords[0]
				y_min = newcoords[1]

				x_max = newcoords[2]
				y_max = newcoords[3]


				if x_max > quads_images.shape[1]:
					x_max = quads_images.shape[1]

				if y_max > quads_images.shape[0]:
					y_max = quads_images.shape[0]


				ww, hh = x_max-x_min, y_max-y_min
				xc = x_min + ww/2
				yc = y_min + hh/2


				xc /= quads_images.shape[1]
				yc /= quads_images.shape[0]

				ww /= quads_images.shape[1]
				hh /= quads_images.shape[0]

				write_txt("labels/{}.txt".format(new_name[:-4]), [class_num, xc, yc, ww, hh])				#xc/quad_w, yc/quad_h, ww/quad_w, hh/quad_h])

				if overlay_flag: 

					pt1 = (int(xc*quads_images.shape[1]-ww*quads_images.shape[1]/2), int(yc*quads_images.shape[0]-hh*quads_images.shape[0]/2))
					pt2 = (pt1[0]+int(ww*quads_images.shape[1]), pt1[1]+int(hh*quads_images.shape[0]))
					quads_images = cv2.rectangle(quads_images, pt1, pt2, (0, 255, 0), 1)

					cv2.imwrite(os.path.join('images', new_name), quads_images)
				else:
					cv2.imwrite(os.path.join('images', new_name), quads_images)




			# annotations.append([class_num, x_tl-minc, y_tl-minr, x_br-minc, y_br-minr])
			# cv2.rectangle(img, (x_tl, y_tl), (x_br, y_br), (0, 255, 0), 1)
		
		# for anno in annotations:
		# 	pt1 = (anno[1], anno[2])
		# # 	pt2 = (anno[3], anno[4])
			# gt_boxes.append([xmin,ymin, xmin+ww, ymin+hh])
			# cv2.rectangle(quads_images, pt1, pt2, (255, 0, 255), 1)
		






# annotations = []
# for xml_file in glob.glob(xml_dir + '/*.xml'):
# 	filename = os.path.basename(xml_file)
# 	img = cv2.imread(os.path.join('495/flir', filename[:-3]+'jpg'))
# 	mask = np.uint8(np.zeros(img.shape))


# 	pixel = cv2.imread(os.path.join('495/flir/finish', filename[:-4], 'PixelLabelData', 'Label_1.png'))
# 	print(np.unique(pixel))
# 	tree = ET.parse(xml_file)
# 	root = tree.getroot()
# 	for member in root.findall('object'):
# 		value = (root.find('filename').text,
# 				 int(root.find('size')[0].text),
# 				 int(root.find('size')[1].text), member[0].text,
# 				 int(member[4][0].text), int(member[4][1].text),
# 				 int(member[4][2].text), int(member[4][3].text))
# 		class_name = member[0].text
# 		x_tl, y_tl, x_br, y_br = int(member[4][0].text), int(member[4][1].text),int(member[4][2].text), int(member[4][3].text)
# 		# cv2.rectangle(img, (x_tl, y_tl), (x_br, y_br), (0, 255, 0), 1)

# 		mask[y_tl:y_br, x_tl:x_br, :] = img[y_tl:y_br, x_tl:x_br, :]
	
# 	thresh = cv2.inRange(mask, (0, 30, 0), (255, 130, 255))
# 	pixel[thresh == 255] = 4
# 	print(np.unique(pixel))
# 	cv2.imwrite(os.path.join('masks', '495_'+filename[:-3]+'png'), pixel)
# 	# cv2.waitKey(0)
# 		# annotations.append(value)

# # print(annotations)

