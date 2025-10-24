import User as U
############## TESTING ##############


test1 = U.UserProfile()

#Confirm set name works
expected = "TestJane1"
test1.setUserName("TestJane1")
result = test1.getUserName()
if result != expected:
    print("Setting username failed, expected: ", expected, "got ", result)
else:
    print("Username is set. expected: ", expected, "result: ", result)

#Confirm set e-mail works
expected = "jane123@email.com"
test1.setEmail("jane123@email.com")
result = test1.getEmail()
if result != expected:
    print("Setting email failed, expected: ", expected, "got ", result)
else:
    print("Email is set. expected: ", expected, "result: ", result)

#Confirm set password works
expected = "JanePassword$"
test1.setPassword("JanePassword$")
result = test1.getPassword()
if result != expected:
    print("Setting password failed, expected: ", expected, "got ", result)
else:
    print("Password is set. expected: ", expected, "result: ", result)

#Confirm set userID works
expected = 1
test1.setUserId(1)
result = test1.getUserId()
if result != expected:
    print("Setting userID failed, expected: ", expected, "got ", result)
else:
    print("Username is set. expected: ", expected, "result: ", result)
