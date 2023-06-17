import time

start = time.time()

i=1
while True:
    end = time.time()
    if end-start > 1.0:
        break
    i+=1

result = 6*(10**23) / i

print('1초당 연산 횟수 : {}'.format(i))
print('아보가드르 넘버 세는데까지 {:.2f}초 걸림'.format(result))