import re   
  
regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'  
  
def checkInvalid(email):   
  
    if(re.search(regex,email)):   
        return False
    else:   
        return True
def registerInputValidate(name,email,password,confirmPassword):
    errors={}
    if name.strip()=='':
        errors['name']="Name must not be empty"
    if email.strip() == '':
        errors['email'] = 'Email must not be empty'
    else:
        if checkInvalid(email):
            errors['email'] = 'Email must be a valid email address';
    if password.strip() == '':
        errors['password'] = 'Password must not be empty'
    elif password!=confirmPassword:
        errors['password'] = 'Password must be equal'
    
    return errors,len(errors.keys())>0
def loginInputValidate(email,password):
    errors={}
    
    if email.strip() == '':
        errors['email'] = 'Email must not be empty'
    else:
        if checkInvalid(email):
            errors['email'] = 'Email must be a valid email address';
    if password.strip() == '':
        errors['password'] = 'Password must not be empty'
    
    return errors,len(errors.keys())>0
    
  
def updateUserValidate(updateUser):
    errors={}
    if "name" in updateUser.keys():
           if updateUser["name"].strip()=='':
                errors['name']="Name must not be empty"
    if "linkedInToken" in updateUser.keys():
           if updateUser["linkedInToken"].strip()=='':
                errors['linkedInToken']="linkedInToken must not be empty"
    if "mailServer" in updateUser.keys():
           if updateUser["mailServer"].strip()=='':
                errors['mailServer']="mailServer must not be empty"
    if "mailServerUserName" in updateUser.keys():
           if updateUser["mailServerUserName"].strip()=='':
                errors['mailServerUserName']="mailServerUserName must not be empty"
    if "mailServerPassword" in updateUser.keys():
           if updateUser["mailServerPassword"].strip()=='':
                errors['mailServerPassword']="mailServerPassword must not be empty"
    
    
    
    return errors,len(errors.keys())>0
def changePasswordValidate(prevPassword,password,confirmPassword):
    errors={}
    if prevPassword.strip()=='':
            errors['prevPassword']="Previous Password must not be empty"

    if password.strip()=='':
        errors['password']="New Password must not be empty"
    elif password!=confirmPassword:
        errors['password'] = 'Password must be equal'
    
    return errors,len(errors.keys())>0

def sendMessageValidate(messageText,profileLink):
    errors={}
    if messageText.strip()=='':
                errors['messageText']="Message text must not be empty"
    
    if profileLink.strip()=='':
        errors['profileLink']="Profile link must not be empty"
    
    return errors,len(errors.keys())>0
def sendConnectValidate(profileLink):
    errors={}
    if profileLink.strip()=='':
        errors['profileLink']="Profile link must not be empty"
    
    return errors,len(errors.keys())>0