import asyncio
import time
import dill
import os
main_dir = os.path.join(os.getcwd(), "dill_test.pkl")
# print(main_dir)
#
#
# u= input("CHOOSE Y OR N:  ").lower()
# if u=="y" :
#     dill.load_session(main_dir)
# s=0
# if u=="ok":
#     s=50000
# d=[]
# if s:
#     print(s)
# for i in range (2):
#     try:
#         print (i)
#         time.sleep(1)
#         d.append(i)
#     except Exception as e:
#         print (e)
#     finally:
#         dill.dump_session(main_dir)





async def async_bar():
    print("async_bar started")
    await asyncio.sleep(2)
    print("async_bar done")


async def async_foo():
    print("async_foo started")
    await asyncio.sleep(2)
    print("async_foo done")

async def main():
    asyncio.ensure_future(async_foo())  # fire and forget async_foo()
    asyncio.ensure_future(async_bar())
    print('Do some actions 1')
    await asyncio.sleep(5)
    print('Do some actions 2')

loop = asyncio.new_event_loop()
loop.run_until_complete(main())
print("aasdasdads")
# asyncio.run(main())