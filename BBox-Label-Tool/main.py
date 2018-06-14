#-------------------------------------------------------------------------------
# Name:        Object bounding box label tool
# Purpose:     Label object bboxes for ImageNet Detection data
# Author:      Qiushi
# Created:     06/06/2014

#
#-------------------------------------------------------------------------------
from __future__ import division
from Tkinter import *
import Tkinter as tk
import tkMessageBox
from PIL import Image, ImageTk
import os
import glob
import random
import os.path
from os import walk, getcwd
import glob

import sys


# colors for the bboxes
COLORS = ['red', 'blue', 'yellow', 'pink', 'cyan', 'green', 'black']
# image sizes for the examples
SIZE = 256, 256




def convert(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)

def setClassNumber(number):
    command = "sed -i '/^[0-9]/ s/./" + str(number) + "/' Labels/" + str(number) + "_YOLO/*.txt"
    print command
    os.system(command)

class LabelTool():
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.title("LabelTool")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width = FALSE, height = FALSE)

        # initialize global state
        self.imageDir = ''
        self.imageList= []
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = 0
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None
        self.Class = ''

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.hl = None
        self.vl = None

        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.label = Label(self.frame, text = "Image Dir:")
        self.label.grid(row = 0, column = 0, sticky = E)
        #self.entry = Entry(self.frame)
        #self.entry.grid(row = 0, column = 1, sticky = W+E)


        dir = os.listdir('./Images')

        self.dropVar=StringVar()
        self.dropVar.set(dir[0])

        self.dropDir = OptionMenu(self.frame, self.dropVar, *dir, command=self.loadDir)
        self.dropDir.config(width=20)

        self.dropDir.grid(row=0, column=1, sticky=W)

        self.generate = Button(self.frame, text='Generate Train/Test', command=self.generateFile)
        self.generate.grid(row = 0, column = 1, sticky = E)

        self.convert = Button(self.frame, text='Convert to YOLO', width=10, command=self.bboxToYolo)
        self.convert.grid(row = 0, column = 2, sticky = W)



        #self.ldBtn = Button(self.frame, text = "Load", command = self.loadDir)
        #self.ldBtn.grid(row = 0, column = 2, sticky = W+E)

        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross')
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        self.parent.bind("<Escape>", self.cancelBBox)  # press <Espace> to cancel current bbox
        self.parent.bind("s", self.cancelBBox)
        self.parent.bind("a", self.prevImage) # press 'a' to go backforward
        self.parent.bind("d", self.nextImage) # press 'd' to go forward
        self.mainPanel.grid(row = 1, column = 1, rowspan = 4, sticky = W+N)

        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text = 'Bounding boxes:')
        self.lb1.grid(row = 1, column = 2,  sticky = W+N)
        self.listbox = Listbox(self.frame, width = 22, height = 10)
        self.listbox.grid(row = 2, column = 2, sticky = N)

        self.btnDel = Button(self.frame, text = 'Delete', command=self.delBBox)
        self.btnDel.grid(row = 3, column = 2, sticky = W+E+N)

        self.btnClear = Button(self.frame, text = 'ClearAll', command=self.clearBBox)
        self.btnClear.grid(row = 4, column = 2, sticky = W+E+N)



        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row = 5, column = 1, columnspan = 2, sticky = W+E)



        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width = 10, command = self.prevImage)
        self.prevBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width = 10, command = self.nextImage)
        self.nextBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.progLabel = Label(self.ctrPanel, text = "Progress:     /    ")
        self.progLabel.pack(side = LEFT, padx = 5)
        self.tmpLabel = Label(self.ctrPanel, text = "Go to Image No.")
        self.tmpLabel.pack(side = LEFT, padx = 5)
        self.idxEntry = Entry(self.ctrPanel, width = 5)
        self.idxEntry.pack(side = LEFT)
        self.goBtn = Button(self.ctrPanel, text = 'Go', command = self.gotoImage)
        self.goBtn.pack(side = LEFT)

        # example pannel for illustration
        self.egPanel = Frame(self.frame, border = 10)
        self.egPanel.grid(row = 1, column = 0, rowspan = 5, sticky = N)
        self.tmpLabel2 = Label(self.egPanel, text = "Examples:")
        self.tmpLabel2.pack(side = TOP, pady = 5)
        self.egLabels = []
        for i in range(3):
            self.egLabels.append(Label(self.egPanel))
            self.egLabels[-1].pack(side = TOP)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side = RIGHT)

        self.frame.columnconfigure(1, weight = 1)
        self.frame.rowconfigure(4, weight = 1)

        # for debugging
##        self.setImage()
##        self.loadDir()

    def setClassName(self):
        self.Class = self.entryClass.get()

        # Current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Directory where the data will reside, relative to 'darknet.exe'
        final_path = 'data/'+self.Class+'/'
        path_data = 'Labels/'+ str(self.category)

        print final_path
        print path_data

        # Percentage of images to be used for the test set
        percentage_test = 10;

        # Create and/or truncate train.txt and test.txt
        file_train = open('train_'+self.Class+'.txt', 'w')
        file_test = open('test_'+self.Class+'.txt', 'w')

        # Populate train.txt and test.txt
        counter = 1
        index_test = round(100 / percentage_test)
        for pathAndFilename in glob.iglob(os.path.join(path_data, "*.txt")):
            title, ext = os.path.splitext(os.path.basename(pathAndFilename))

            if counter == index_test:
                counter = 1
                file_test.write(final_path + title + '.JPEG' + "\n")
            else:
                file_train.write(final_path + title + '.JPEG' + "\n")
                counter = counter + 1


        self.windowClass.destroy()




    def generateFile(self):

        self.windowClass = tk.Toplevel(root)
        self.labelClass = Label(self.windowClass, text = "Class name : ")
        self.labelClass.grid(row = 0, column = 0, sticky = W+E,pady = 10,padx=10)

        self.entryClass = Entry(self.windowClass)
        self.entryClass.grid(row = 0, column = 1, sticky = W+E,pady = 10,padx=10)

        self.goBtn = Button(self.windowClass, text = 'Ok', command = self.setClassName)
        self.goBtn.grid(row = 1, column = 1,sticky = E, padx =10)




    def loadDir(self, value):

        s = str(value)
        self.parent.focus()
        self.category = s

        # get image list
        self.imageDir = os.path.join(r'./Images', '%s' %(self.category))
        print self.imageDir
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.JPEG'))
        if len(self.imageList) == 0:
            print 'No .JPEG images found in the specified dir!'
            return

        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)

         # set up output dir
        self.outDir = os.path.join(r'./Labels', '%s' %(self.category))
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)

        # load example bboxes
        self.egDir = './Examples'
        if not os.path.exists(self.egDir):
            return
        filelist = glob.glob(os.path.join(self.egDir, '*.JPEG'))
        self.tmp = []
        self.egList = []
        random.shuffle(filelist)
        for (i, f) in enumerate(filelist):
            if i == 3:
                break
            im = Image.open(f)
            r = min(SIZE[0] / im.size[0], SIZE[1] / im.size[1])
            new_size = int(r * im.size[0]), int(r * im.size[1])
            self.tmp.append(im.resize(new_size, Image.ANTIALIAS))
            self.egList.append(ImageTk.PhotoImage(self.tmp[-1]))
            self.egLabels[i].config(image = self.egList[-1], width = SIZE[0], height = SIZE[1])

        self.loadImage()
        print '%d images loaded from %s' %(self.total, s)

    def loadImage(self):
        # load image
        imagepath = self.imageList[self.cur - 1]
        self.img = Image.open(imagepath)
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), 400), height = max(self.tkimg.height(), 400))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
        self.progLabel.config(text = "%04d/%04d" %(self.cur, self.total))

        # load labels
        self.clearBBox()
        self.imagename = os.path.split(imagepath)[-1].split('.')[0]
        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        bbox_cnt = 0
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    if i == 0:
                        bbox_cnt = int(line.strip())
                        continue
                    tmp = [int(t.strip()) for t in line.split()]
##                    print tmp
                    self.bboxList.append(tuple(tmp))
                    tmpId = self.mainPanel.create_rectangle(tmp[0], tmp[1], \
                                                            tmp[2], tmp[3], \
                                                            width = 2, \
                                                            outline = COLORS[(len(self.bboxList)-1) % len(COLORS)])
                    self.bboxIdList.append(tmpId)
                    self.listbox.insert(END, '(%d, %d) -> (%d, %d)' %(tmp[0], tmp[1], tmp[2], tmp[3]))
                    self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])

    def saveImage(self):
        with open(self.labelfilename, 'w') as f:
            f.write('%d\n' %len(self.bboxList))
            for bbox in self.bboxList:
                f.write(' '.join(map(str, bbox)) + '\n')
        print 'Image No. %d saved' %(self.cur)


    def mouseClick(self, event):
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
        else:
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            self.bboxList.append((x1, y1, x2, y2))
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.listbox.insert(END, '(%d, %d) -> (%d, %d)' %(x1, y1, x2, y2))
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
        self.STATE['click'] = 1 - self.STATE['click']

    def mouseMove(self, event):
        self.disp.config(text = 'x: %d, y: %d' %(event.x, event.y))
        if self.tkimg:
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width = 2)
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width = 2)
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
            self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'], \
                                                            event.x, event.y, \
                                                            width = 2, \
                                                            outline = COLORS[len(self.bboxList) % len(COLORS)])

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        self.mainPanel.delete(self.bboxIdList[idx])
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []

    def prevImage(self, event = None):
        self.saveImage()
        if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    def nextImage(self, event = None):
        self.saveImage()
        if self.cur < self.total:
            self.cur += 1
            self.loadImage()

    def gotoImage(self):
        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:
            self.saveImage()
            self.cur = idx
            self.loadImage()



    def bboxToYolo(self):

        classes = [self.category]

        print "Class #" + self.category

        cls = self.category
        if cls not in classes:
            exit(0)
        cls_id = classes.index(cls)

        """ Configure Paths"""
        cur_dir = os.getcwd()
        mypath = "Labels/" + str(cls) + "/"
        outpath = "Labels/" + str(cls) + "_YOLO/"

        print mypath, outpath

        wd = getcwd()
        list_file = open('%s/%s_list.txt' % (wd, cls), 'w')

        """ Get input text file list """
        txt_name_list = []

        for (dirpath, dirnames, filenames) in walk(mypath):
            txt_name_list.extend(filenames)
            break
        print(txt_name_list)

        """ Process """
        for txt_name in txt_name_list:
            # txt_file =  open("Labels/stop_sign/001.txt", "r")

            """ Open input text files """
            txt_path = mypath + txt_name
            print("Input:" + txt_path)
            txt_file = open(txt_path, "r")
            lines = txt_file.read().split('\n')  # for ubuntu, use "\r\n" instead of "\n"

            out_dir = os.path.join(cur_dir, outpath)
            print out_dir

            if not os.path.exists(os.path.dirname(out_dir)):
                try:
                    os.makedirs(os.path.dirname(out_dir))
                except OSError as exc:  # Guard against race condition
                    exit(1)

            """ Open output text files """
            txt_outpath = outpath + txt_name
            print("Output:" + txt_outpath)
            txt_outfile = open(txt_outpath, "w")

            """ Convert the data to YOLO format """
            ct = 0
            for line in lines:
                # print('lenth of line is: ')
                # print(len(line))
                # print('\n')
                if (len(line) >= 2):
                    ct = ct + 1
                    print(line + "\n")
                    elems = line.split(' ')
                    print(elems)
                    xmin = elems[0]
                    xmax = elems[2]
                    ymin = elems[1]
                    ymax = elems[3]
                    #
                    img_path = str('%s/Images/%s/%s.JPEG' % (wd, cls, os.path.splitext(txt_name)[0]))
                    # t = magic.from_file(img_path)
                    # wh= re.search('(\d+) x (\d+)', t).groups()
                    im = Image.open(img_path)
                    w = int(im.size[0])
                    h = int(im.size[1])
                    # w = int(xmax) - int(xmin)
                    # h = int(ymax) - int(ymin)
                    # print(xmin)
                    print(w, h)
                    b = (float(xmin), float(xmax), float(ymin), float(ymax))
                    bb = convert((w, h), b)
                    print(bb)
                    txt_outfile.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')

            """ Save those images with bb into list"""
            if (ct != 0):
                list_file.write('%s/Images/%s/%s.JPEG\n' % (wd, cls, os.path.splitext(txt_name)[0]))

        list_file.close()

        setClassNumber(cls)

    ##    def setImage(self, imagepath = r'test2.png'):
##        self.img = Image.open(imagepath)
##        self.tkimg = ImageTk.PhotoImage(self.img)
##        self.mainPanel.config(width = self.tkimg.width())
##        self.mainPanel.config(height = self.tkimg.height())
##        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)

if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.resizable(width =  True, height = True)
    root.mainloop()
