import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
import tkinter.messagebox
from shapely.geometry import box as shapelyBox
from tensorflow import keras
from sklearn.preprocessing import LabelEncoder
import numpy as np
import webbrowser
import tkinter.font as tkFont
import cv2 as cv
from PIL import Image, ImageTk, ImageGrab
import json

import os
import io

categoriesList = []
data = {}
updateId = {}

imageWidth = 300
imageheight = 300
filePath = ""
categorie = ""
x_start = 0
y_start = 0
x_end = 0
y_end = 0
annotationsSaved = True
pil_image = ""


# functions


def chargeCategories():
    categoriesList.append("Mask")
    categoriesList.append("No-Mask")


chargeCategories()


def open_file():
    global imageArea
    global filePath
    global pil_image

    if len(selectedBoxes.winfo_children()) != 0 and annotationsSaved == False:
        MsgBox = tk.messagebox.askquestion(
            "unsaved Annotations",
            "you have unsaved annotations , do you want to save them ?",
            icon="warning",
        )
        if MsgBox == "yes":
            saveAnnotation()
    for child in selectedBoxes.winfo_children():
        child.destroy()
    data.clear()

    filePath = tkinter.filedialog.askopenfile(
        mode="rb",initialdir='../img/dataset',
        title="Select an image",
        filetypes=[ ("png file", "*.png"),("jpg file", "*.jpg")],
    )

    if filePath:
        pil_image = Image.open(filePath).resize(
            (imageWidth, imageheight), Image.ANTIALIAS
        )
        img = ImageTk.PhotoImage(pil_image)
        app.img = img
        imageArea.delete("all")
        imageArea.create_image(0, 0, image=img, anchor=tk.NW)
        imageArea.pack()
        boxSelection["state"] = tk.NORMAL


def selectAbox():
    global imageArea
    global x_start
    global y_start
    global x_end
    global y_end
    global filePath

    # Read image

    opencvImage = cv.cvtColor(np.array(pil_image), cv.COLOR_RGB2BGR)
    # Select ROI
    r = cv.selectROI("select the area", opencvImage)
    x_start = r[0]
    y_start = r[1]
    x_end = r[0] + r[2]
    y_end = r[1] + r[3]
    cv.destroyAllWindows()

    # create box
    createBoxElement("", x_start, y_start, x_end, y_end)


def createRectangleCanvas(x1, y1, x2, y2):
    global imageArea

    rectangleID = imageArea.create_rectangle(x1, y1, x2, y2, width=2)
    imageArea.create_text(x1,y1-10,text="box : " + str(rectangleID),anchor="w",tags="label"+str(rectangleID))

    return rectangleID


def createBoxElement(categorie, x_start, y_start, x_end, y_end):
    global categorie_input
    global x_start_input
    global y_start_input
    global x_end_input
    global y_end_input
    global inputForm

    inputForm = tk.LabelFrame(rightFrame, text="input form ")

    # input filed
    categorie_input = ttk.Combobox(inputForm, state="readonly", values=categoriesList)
    categorie_input.set(categorie)
    categorie_input.grid(row=0, column=1)

    x_start_input = tk.Entry(inputForm)
    x_start_input.insert(tk.END, x_start)
    x_start_input.grid(row=1, column=1)

    y_start_input = tk.Entry(inputForm)
    y_start_input.insert(tk.END, y_start)
    y_start_input.grid(row=2, column=1)

    x_end_input = tk.Entry(inputForm)
    x_end_input.insert(tk.END, x_end)
    x_end_input.grid(row=3, column=1)

    y_end_input = tk.Entry(inputForm)
    y_end_input.insert(tk.END, y_end)
    y_end_input.grid(row=4, column=1)

    addBox = tk.Button(
        inputForm,
        text="add Box",
        bg="#676FA3",
        fg="white",
        command=lambda: saveBoxData(
            categorie_input.get(),
            x_start_input.get(),
            y_start_input.get(),
            x_end_input.get(),
            y_end_input.get(),
        ),
    )
    addBox.grid(row=5, column=0, columnspan=2, sticky="nesw")

    # labels
    categorie_label = tk.Label(inputForm, text="categorie")
    categorie_label.grid(row=0, column=0)

    x_start_label = tk.Label(inputForm, text="x_start")
    x_start_label.grid(row=1, column=0)
    y_start_label = tk.Label(inputForm, text="y_start")
    y_start_label.grid(row=2, column=0)

    x_end_label = tk.Label(inputForm, text="x_end")
    x_end_label.grid(row=3, column=0)
    y_end_label = tk.Label(inputForm, text="y_end")
    y_end_label.grid(row=4, column=0)

    inputForm.pack()


def saveBoxData(categorie, x1, y1, x2, y2):
    global data
    global annotationsSaved

    # verif overlap with other boxes

    if verifOverlap(int(x1), int(y1), int(x2), int(y2)):
        tkinter.messagebox.showerror(
            "Overlap Error",
            " this box Overlap with other Boxes with more than 20% \n or the box surface is less than 40 pixels ",
        )
    elif verifDimensions(int(x1), int(y1), int(x2), int(y2)) :

        tkinter.messagebox.showerror(
                "Bad Dimensions ",
                " To Avoid classify outliers , you should select a box with sides between 120 and 180px \n for more details please see Documentation !",
        )
    else:
        # create canavs rectangle
        id = createRectangleCanvas(int(x1), int(y1), int(x2), int(y2))
        # update data file
        data[id] = {"category": categorie, "x1": x1, "y1": y1, "x2": x2, "y2": y2}

        # show new entry
        showSelectedBoxe(id, data.get(id))
        annotationsSaved = False
    # delete input form
    inputForm.destroy()


def showSelectedBoxe(id, boxData):
    # create one selected box

    oneSelectedBox = tk.LabelFrame(
        selectedBoxes, text="box : " + str(id), pady=5, bg="white", borderwidth=1
    )
    oneSelectedBox.idTag = id
    info = tk.Label(oneSelectedBox, text=",".join(list(boxData.values())), bg="white")
    updateButton = tk.Button(oneSelectedBox,text="Update",bg="#676FA3",fg="white", name=str(id)
                             ,command=lambda: updateOneBox(id, oneSelectedBox))
    DeleteButton = tk.Button(oneSelectedBox, text="Delete", bg="#676FA3", fg="white"
                             , command=lambda: deleteOneBox(id, oneSelectedBox))

    info.grid(row=0, column=0, sticky=tk.W)
    updateButton.grid(row=0, column=1)
    DeleteButton.grid(row=0, column=2)

    # add one selected box to the frame selectedBoxes
    oneSelectedBox.pack()
    oneSelectedBox.columnconfigure(0, minsize=200)
    oneSelectedBox.columnconfigure(1, minsize=50)
    oneSelectedBox.columnconfigure(2, minsize=50)

def deleteOneBox(id, frameParent):
    # Delete old rectangle in canvas
    imageArea.delete(str(id))
    # Delete label of old rectangle in canvas
    imageArea.delete("label"+str(id))

    # delete data from old dictionary data
    data.pop(id)
    # delete old boxelement
    frameParent.destroy()



def updateOneBox(id, frameParent):
    global categorie
    global x_start
    global y_start
    global x_end
    global y_end
    global imageArea
    global data

    categorie = data.get(id).get("category")
    x_start = data.get(id).get("x1")
    y_start = data.get(id).get("y1")
    x_end = data.get(id).get("x2")
    y_end = data.get(id).get("y2")

    # Delete old rectangle in canvas
    imageArea.delete(str(id))
    # Delete label of old rectangle in canvas
    imageArea.delete("label"+str(id))

    # delete data from old dictionary data
    data.pop(id)

    # create input form to update data
    createBoxElement(categorie, x_start, y_start, x_end, y_end)

    # delete old boxelement
    frameParent.destroy()


def saveAnnotation():
    global annotationsSaved
    imageData = {}

    # Opening JSON file
    try:
        with open("annotations.json") as infile:
            imageData = json.load(infile)
        infile.close()
    except:
        imageData = {
            "urlImage": {
                "boxId": {"category": "", "x1": "", "y1": "", "x2": "", "y2": ""}
            }
        }

    # Data to be written
    if filePath:
        with open("annotations.json", "w") as outfile:
            imageData[filePath.name] = data
            json.dump(imageData, outfile)
        annotationsSaved = True

        tkinter.messagebox.showinfo(
            "Save Annotation",
            str(len(data))
            + " Annotations have been successfully saved in annotations.json",
        )
    else:
        tkinter.messagebox.showerror(
            "Error Save annotation ",
            "Something went wrong ! please verify that your image is uploaded",
        )


def importCategories():
    global categoriesList
    # Opening JSON file
    pathFileCategories = tkinter.filedialog.askopenfile(
        mode="rb", title="Import Categories", filetypes=[("json file", "*.json")]
    )
    if pathFileCategories:
        f = open(
            pathFileCategories.name,
        )
        # returns JSON object as a dictionary
        categorieDictionary = json.load(f)

    try:
        nbCategries = len(categorieDictionary["categories"])
        # append all the categories in the file to the current list of categories
        categoriesList.extend(categorieDictionary["categories"])
        # Remove any duplicates from the List
        categoriesList = list(dict.fromkeys(categoriesList))
        # Closing file
        f.close()
        tkinter.messagebox.showinfo(
            "Import  Categories",
            str(nbCategries) + " Categories have been successfully imported",
        )
    except:
        tkinter.messagebox.showerror(
            "Error Import  Categories",
            "Something went wrong ! please verify that your json file in this format \n {'categories':['category1','category1','category_n']}",
        )


def addCategoryGui():
    addCategoryForm = tk.LabelFrame(leftFrame, text="add Category")

    newCategoryInput = tk.Entry(addCategoryForm)
    newCategoryInput.pack()
    addCategoryBtn = tk.Button(
        addCategoryForm,
        text="add",
        bg="#676FA3",
        fg="white",
        command=lambda: addCategoryFn(newCategoryInput.get(), addCategoryForm),
    )
    addCategoryBtn.pack(fill=tk.X, pady=5)

    addCategoryForm.pack()


def addCategoryFn(newCategory, parent):
    global categoriesList
    if newCategory:
        categoriesList.append(newCategory)
        # remove duplicate
        categoriesList = list(dict.fromkeys(categoriesList))
        tkinter.messagebox.showinfo(
            "add  Category", newCategory + " have been successfully added"
        )

    # destroy form
    parent.destroy()


def deleteCategoryGui():
    deleteCategoryForm = tk.LabelFrame(leftFrame, text="delete a Category :")

    # selected category to be deleted
    deletedCategoryLabel = tk.Label(
        deleteCategoryForm, text="category to be deleted :", anchor="w"
    )
    deletedCategoryLabel.pack(fill=tk.X)
    categorie_input = ttk.Combobox(
        deleteCategoryForm, state="readonly", values=categoriesList
    )
    categorie_input.current(1)
    categorie_input.pack()

    # get the category to be replaced
    deleteCategoryBtn = tk.Button(
        deleteCategoryForm,
        text="delete",
        bg="#676FA3",
        fg="white",
        command=lambda: replaceCategoryFn(
            " ", categorie_input.get(), deleteCategoryForm, "deleted"
        ),
    )
    deleteCategoryBtn.pack(fill=tk.X, pady=5)

    deleteCategoryForm.pack()


def replaceCategoryGui():
    replaceCategoryForm = tk.LabelFrame(leftFrame, text="replace a Category :")

    # selected category to be replaced
    replacedCategoryLabel = tk.Label(
        replaceCategoryForm, text="category to be replaced :", anchor="w"
    )
    replacedCategoryLabel.pack(fill=tk.X)
    categorie_input = ttk.Combobox(
        replaceCategoryForm, state="readonly", values=categoriesList
    )
    categorie_input.current(1)
    categorie_input.pack()

    # input new category
    newCategoryLabel = tk.Label(replaceCategoryForm, text="new category", anchor="w")
    newCategoryLabel.pack(fill=tk.X)
    newCategoryInput = tk.Entry(replaceCategoryForm)
    newCategoryInput.pack(fill=tk.X)

    # get the category to be replaced
    replaceCategoryBtn = tk.Button(
        replaceCategoryForm,
        text="replace",
        bg="#676FA3",
        fg="white",
        command=lambda: replaceCategoryFn(
            newCategoryInput.get(),
            categorie_input.get(),
            replaceCategoryForm,
            "replaced by",
        ),
    )
    replaceCategoryBtn.pack(fill=tk.X, pady=5)

    replaceCategoryForm.pack()


def replaceCategoryFn(newCategory, oldCategory, parent, operation):
    global categoriesList
    global data
    if newCategory:
        compteur = 0
        # delete old category from list of the category
        categoriesList.remove(oldCategory)
        # add the new one
        categoriesList.append(newCategory)

        for key, value in data.items():
            if value.get("category") == oldCategory:
                value["category"] = newCategory
                compteur += 1
        for child in selectedBoxes.winfo_children():
            child.winfo_children()[0]["text"] = ",".join(
                list(data.get(child.idTag).values())
            )

        tkinter.messagebox.showinfo(
            "replace  Category",
            str(compteur)
            + " occurrences of "
            + oldCategory
            + " were successfully "
            + operation
            + " "
            + newCategory,
        )

    # destroy form
    parent.destroy()

# verif if the boxes sides are between 120 and 180px to avoid classify outliers
def verifDimensions(XA1, YA1, XA2, YA2):
    return  ((XA2-XA1) <100) or ((XA2-XA1) > 300 ) or ((YA2-YA1) <100) or ((YA2-YA1) > 300)


# determine if two boxes overlap or not and how much the overlap
def verifOverlap(XA1, YA1, XA2, YA2):
    isOverlap = False
    A = shapelyBox(XA1, YA1, XA2, YA2)
    for box in data.values():
        # create shapely box for every rectangle
        XB1, YB1, XB2, YB2 = (
            int(box["x1"]),
            int(box["y1"]),
            int(box["x2"]),
            int(box["y2"]),
        )
        B = shapelyBox(XB1, YB1, XB2, YB2)

        # surface Boxe A
        SA = A.area
        # surface Boxe B
        SB = B.area
        # intersection size
        SI = A.intersection(B).area

        if A.intersects(B):

            if SI > (0.2 * SA) or SI > (0.2 * SB):
                isOverlap = True

    return isOverlap

def PredictImage():
    predict(filePath,'category')



def predict(filePath , mode):
    green =  '\033[1;37;42m'
    red =    '\033[1;37;41m'
    import cv2
    import numpy as np
    imageWidth = 64
    imageHeight = 64

    #load model

    model = keras.models.load_model('my_model')
    model.load_weights("weights.h5")
    label_encoder = LabelEncoder()
    label_encoder.classes_ = np.load(r'C:\Users\autre\Desktop\nnl2\classes.npy')

    imgOriginal = cv.cvtColor(np.array(pil_image), cv.COLOR_RGB2BGR)
    img = np.asarray(imgOriginal)
    img = cv2.resize(img, (imageWidth, imageHeight))
    img = img / 255
    img=img.reshape(1,imageWidth,imageWidth,3)




    prediction = model.predict(img)
    if(mode == "category"):

        probVal = np.amax(model.predict(img))

        category = label_encoder.inverse_transform([int(np.argmax(prediction[0]))])[0]
        print(category)
        if category == 'without_mask' :
            colortext =(0,0,220)
        else :

            colortext =(0,245,128)

        cv2.putText(imgOriginal,str(category) +" "+str(probVal),(0,50),cv2.FONT_HERSHEY_COMPLEX,1,colortext,2)

    elif(mode == "probabilites"):
        probabilites = {}
        i = 0
        for probability in prediction[0]:
            probabilites[label_encoder.inverse_transform([int(prediction[0][i])])[0]]=str(round(float("{:.8f}".format(float(probability))), 2) * 100)+'%'

            i += 1
        print(probabilites)
    else:
        print("Mode not recognized")

# windows
app = tk.Tk()
app.title("ImageAnnotator")
app.minsize(1020, 700)
width_value = app.winfo_screenwidth()
height_value = app.winfo_screenheight()
app.geometry(str(width_value) + "x" + str(height_value))

app.columnconfigure(0, minsize=150)
app.columnconfigure(1, minsize=900)
app.columnconfigure(2, minsize=300)

# frames

leftFrame = tk.LabelFrame(app, text="left", background="#EEF2FF", width=150, height=700)
middleFrame = tk.LabelFrame(
    app, text="middle", background="#EEF2FF", width=900, height=700
)
rightFrame = tk.LabelFrame(
    app, text="right", background="#EEF2FF", width=300, height=700
)

# lefFrame

uploadButon = tk.Button(
    leftFrame, text="upload Image", fg="white", bg="#676FA3", command=open_file
)
uploadButon.pack(ipadx=200, ipady=10)
annotationSaving = tk.Button(
    leftFrame, text="save annotation", fg="white", bg="#676FA3", command=saveAnnotation
)
annotationSaving.pack(ipadx=200, ipady=10)
importCategories = tk.Button(
    leftFrame,
    text="import categories",
    fg="white",
    bg="#676FA3",
    command=importCategories,
)
importCategories.pack(ipadx=200, ipady=10)
addCategory = tk.Button(
    leftFrame, text="add category", fg="white", bg="#676FA3", command=addCategoryGui
)
addCategory.pack(ipadx=200, ipady=10)
deleteCategory = tk.Button(
    leftFrame,
    text="delete category",
    fg="white",
    bg="#676FA3",
    command=deleteCategoryGui,
)
deleteCategory.pack(ipadx=200, ipady=10)
replaceCategory = tk.Button(
    leftFrame,
    text="replace category",
    fg="white",
    bg="#676FA3",
    command=replaceCategoryGui,
)
replaceCategory.pack(ipadx=200, ipady=10)
help = tk.Button(
    leftFrame,
    text="help",
    fg="white",
    bg="#676FA3",
    command=lambda: webbrowser.open_new("Documentation.pdf"),
)


help.pack(ipadx=200, ipady=10)



predictBtn = tk.Button(
    leftFrame,
    text="Predict this image",
    fg="white",
    bg="#676FA3",
    command=lambda: PredictImage(),
)


predictBtn.pack(ipadx=200, ipady=10)


# middleFrame
imageArea = tk.Canvas(
    middleFrame, background="white", width=imageWidth, height=imageheight
)
imageArea.pack()

# rightFrame
boxSelection = tk.Button(
    rightFrame,
    text="box selection",
    fg="white",
    bg="#676FA3",
    command=selectAbox,
    state=tk.DISABLED,
)
boxSelection.pack(ipadx=200, ipady=10)

# selected elements / boxes inside a frame in the right frame


selectedBoxes = tk.LabelFrame(rightFrame, text="Selected Boxes", background="#EEF2FF")

selectedBoxes.pack()

# positions
leftFrame.grid(row=0, column=0)
leftFrame.pack_propagate(0)
middleFrame.grid(row=0, column=1)
middleFrame.pack_propagate(0)
rightFrame.grid(row=0, column=2)
rightFrame.pack_propagate(0)

app.mainloop()
