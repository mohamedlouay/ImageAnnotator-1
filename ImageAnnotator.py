from tkinter import *
from tkinter.messagebox import *
from PIL import ImageTk, Image
import json
from shapely.geometry import Polygon

root = Tk()
categories = {}
data = {}
data['Categories'] = []
rectangles = []

image = ImageTk.PhotoImage(Image.open("maks119.png"))
canvas = Canvas(root, width="900", height="900", bg='white')
canvas.grid(column=2, row=1, sticky=N)
img = canvas.create_image(600,200, image=image)

def first_click(event):
    global lastx, lasty
    lastx, lasty = event.x, event.y

def draw_rectangle(event):
    global newx, newy, coordinates, obj
    newx, newy = event.x, event.y
    
    coordinatesLabel = Label(root, text= str(lastx)+' '+str(lasty)+' '+str(event.x)+' '+str(event.y))
    coordinatesLabel.grid(column=2, row=1)
    coordinates = str(lastx)+' , '+str(lasty)+' , '+str(newx)+' , '+str(newy)
    
    rect = Polygon([(lastx,lasty),(lastx,newy), (newx, newy), (newx, lasty)])

    intersect = checkForIntersection(rect)
    if(intersect):
        showerror("Invalid position", "This rectangle intersects with another rectangle for more than '20%' of its area")
    else:
        obj = canvas.create_rectangle((lastx, lasty, newx, newy),width=1)
        rectangles.append(rect)


def checkForIntersection(newRectangle: Polygon) -> bool:
    if(len(rectangles) >= 1):
        for rectangle in rectangles:
            if(rectangle.intersection(newRectangle)):
                condition1 = ((rectangle.intersection(newRectangle).area / rectangle.area) * 100 ) > 20
                condition2 = ((newRectangle.intersection(rectangle).area / newRectangle.area) * 100 ) > 20
                if(condition1 or condition2):
                    return True
    else:
        return False
        
canvas.bind("<Button-1>", first_click)
canvas.bind("<ButtonRelease-1>", draw_rectangle)
root.geometry("1300x1300")

title = Label(root, text="Image Annotator")
title.grid(column=2, row=0)

def addCategories():
    categories[catEntry.get()] = obj
        
    data['Categories'].append({
    'category': catEntry.get(),
    'coordinate': coordinates,
})

def deleteCategory():
    obj = categories.get(catEntryToDelete.get())
    canvas.delete(obj)

catEntry = Entry(root)
catEntry.grid(column=2, row=1, ipadx=20, ipady=6, sticky=E)
addCategory = Button(root, text="add category", command=addCategories)
addCategory.grid(column=3, row=1, ipadx=20, ipady=6, padx=20, sticky=W)

catEntryToDelete = Entry(root)
catEntryToDelete.grid(column=1, row=1, ipadx=20, ipady=6, sticky=E)
categoryToDelte = Button(root, text="delete category", command=deleteCategory)
categoryToDelte.grid(column=2, row=1, ipadx=20, ipady=6, padx=20, sticky=W)

root.mainloop()
print(categories)
json_object = json.dumps(data, indent = 4)

with open('data.json', 'w') as outfile:
    outfile.write(json_object)