# detect gender, age-range, emotion, other attributes like glasses etc.
#Prajwal Adhikari
import boto3
import os
from flaskext.mysql import MySQL
from flask import Flask, render_template, request

app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'test'

mysql = MySQL(app)

app.secret_key = 'pOrgLoVpiI25H38A6wnN9REU8M5FawbvjtGQvX2Q'
bucket_name = "lab3aws"

s3 = boto3.client("s3", aws_access_key_id='ASIAQLQHRPNGJGZDHMND',
aws_secret_access_key='pOrgLoVpiI25H38A6wnN9REU8M5FawbvjtGQvX2Q',
aws_session_token='FwoGZXIvYXdzEHoaDErRlRp0L4DRjmtSRSLbARM91VBXbk6yDa2I376K0LZBeT+s7xrrKKYk6ZMO7abGYlZo03yUD4t77xC4+6tC+I9SJK4jgw/flJw0IveqRhw8cRZCXFFrTlGTG7YDtoEBo6PL2mRxFPsAGkfPI97IyB2KO/bi6mPS40Hc+BsKgXAxv3ZFWhT5AIAakYC0PBibFNWpZkAvJd6+ykNeV78R5THfROC/OrpPCO8no/ctE5AqZ5c5Wgx+NMcVsC+ItptP4ULOFWSeRKwIWaxBaO94p+dX+od3/8ZCc0D2is0dsqcvbulN5xO0AwufZyjgsN37BTItCgoRZM8cd0lidWf89j4dMGfgk/HDcqT5Wby7aFAw924HZcjsrlc3SL89L1eI')
bucket_resource = s3

client = boto3.client("rekognition", aws_access_key_id='ASIAQLQHRPNGJGZDHMND',
aws_secret_access_key='pOrgLoVpiI25H38A6wnN9REU8M5FawbvjtGQvX2Q',
aws_session_token='FwoGZXIvYXdzEHoaDErRlRp0L4DRjmtSRSLbARM91VBXbk6yDa2I376K0LZBeT+s7xrrKKYk6ZMO7abGYlZo03yUD4t77xC4+6tC+I9SJK4jgw/flJw0IveqRhw8cRZCXFFrTlGTG7YDtoEBo6PL2mRxFPsAGkfPI97IyB2KO/bi6mPS40Hc+BsKgXAxv3ZFWhT5AIAakYC0PBibFNWpZkAvJd6+ykNeV78R5THfROC/OrpPCO8no/ctE5AqZ5c5Wgx+NMcVsC+ItptP4ULOFWSeRKwIWaxBaO94p+dX+od3/8ZCc0D2is0dsqcvbulN5xO0AwufZyjgsN37BTItCgoRZM8cd0lidWf89j4dMGfgk/HDcqT5Wby7aFAw924HZcjsrlc3SL89L1eI')



@app.route("/")
def home():
    return render_template("index.html")


@app.route('/analyze', methods=['POST'])
def analyze():
    output = []
    attributes = []
    file = request.files['file1']
    target = os.path.join('./static/', 'file')
    if not os.path.isdir(target):
        os.makedirs(target)
    filename = file.filename
    destination = "/".join([target, filename])
 
    file.save(destination)
    datafile = open(destination, "rb")
    datafile.close()

    destination = "/".join([target, filename])
    bucket_resource.upload_file(
        Bucket=bucket_name,
        Filename=destination,
        Key=destination
    )

    response = client.detect_faces(Image={'S3Object':
                                          {'Bucket': bucket_name,
                                           'Name': destination}},
                                   Attributes=['ALL'])
    for faceDetail in response['FaceDetails']:
        print('The detected face is between ' +
              str(faceDetail['AgeRange']['Low']) +
              ' and ' + str(faceDetail['AgeRange']['High']) +
              ' years old')
        output.append(str(faceDetail['AgeRange']['Low']))
        output.append(str(faceDetail['AgeRange']['High']))
        output.append(str(faceDetail['Gender']['Value']))
        output.append(str(faceDetail['Gender']['Confidence']))
        attributes.append(str(faceDetail['Eyeglasses']['Value']))
        attributes.append(str(faceDetail['Sunglasses']['Value']))
        attributes.append(str(faceDetail['Mustache']['Value']))
        attributes.append(str(faceDetail['Beard']['Value']))
        for emotion in faceDetail['Emotions']:
            output.append((emotion['Confidence']))
            output.append((emotion['Type']))

    sung=[]
    eyeg=[]
    musg=[]
    if attributes[0] == 'True':
        if output[2] == 'Female':
            eyeg.append('She is wearing glasses.')
        else:
            eyeg.append('He is wearing glasses.')
    if attributes[0] == 'True':
        if attributes[1] == 'True':
            if output[2] == 'Female':
                sung.append('She is wearing sunglasses.')
            else:
                sung.append('He is wearing sunglasses.')
    elif output[2] == 'Female' and attributes[1] == 'True':
        sung.append('She is wearing sunglasses.')
    elif output[2] == 'Male' and attributes[1] == 'True':
        sung.append('He is wearing sunglasses.')

    if output[2] == 'Male':
        if attributes[0] == 'True' and attributes[1] == 'True':
            if attributes[3] == 'True':
                if attributes[2] == 'True':
                    musg.append('He has mustache and beard.')
                else:
                    musg.append('He has beard.')
            elif attributes[2] == 'True':
                musg.append('He has mustache.')
        elif attributes[0] == 'True' and attributes[1] == 'False':
            if attributes[3] == 'True':
                if attributes[2] == 'True':
                    musg.append('He has mustache and beard.')
                else:
                    musg.append('He has beard.')
            elif attributes[2] == 'True':
                musg.append('He has mustache.')
        elif attributes[0] == 'False' and attributes[1] == 'False':
            if attributes[3] == 'True':
                if attributes[2] == 'True':
                    musg.append('He has mustache and beard.')
                else:
                    musg.append('He has beard.')
            elif attributes[2] == 'True':
                musg.append('He has mustache.')
        elif attributes[0] == 'False' and attributes[1] == 'True':
            if attributes[3] == 'True':
                if attributes[2] == 'True':
                    musg.append('He has mustache and beard.')
                else:
                    musg.append('He has beard.')
            elif attributes[2] == 'True':
                musg.append('He has mustache.')
    firstName = request.form['username']
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO `test`.`faceanalyze`(username, image, "
                "imagename, gender, genderconfidence, agelower, agehigher)"
                " VALUES (%s, %s,%s, %s, %s, %s, %s)",
                (firstName, destination, filename,
                 str(output[2]), str(output[3]), str(output[0]),
                 str(output[1])))
    conn.commit()
    cur.close()
    prepare = ('Analysis Report:')
    genders = ('Gender of the person is' + ' ' + output[2] ) 
    age = ('The person is  between ' + output[0] + ' and ' + output[1] + ' years old.')
    emotion = ('The emotion state of person is '  + str(output[5] + '.'))
    return render_template("index.html", analyzed_text=prepare,
                           address=filename, genders=genders,
                           age=age, emotion=emotion, sun=sung,
                           eye=eyeg, musg=musg)


if __name__ == "__main__":
    app.run(debug=True)
