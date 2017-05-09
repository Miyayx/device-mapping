## 

> 1. python find_shared_device.py
> 2. python find_private_graph.py
> 3. python cross_ad.py
> 4. python generate_output.py
> 5. 结果统计 result_statistics.py

## 
#### fileio.py
读取data_file的时候，会通过account_minimum, account_maximum, device_maximum过滤掉一部分ad，不作为处理。
其中find_shared_device中删除了账号数量过少和过多的，而find_private_graph中则保留了账号数量少的
账号数量过多的ad，作为非家庭ad，被记录在bad_ads.dat

#### find_shared_device.py
输入：被过滤后的ad及其行为和账号信息
输出：1. ad下的共享设备；2. 共享设备数量多，被判定成的非家庭ad
注:本步还生成bad_ads.dat

#### find_private_graph.py
输入：
1. 过滤了账号数量过多和设备数量过多的ad, 及其行为和账号信息
2. 共享设备（过滤用，这部分设备不拿来计算）
3. 非家庭AD（过滤用，这部分ad不拿来计算)

输出：
AD及其子图，每个子图一行

#### cross_ad.py
1. 找到有同一账号出现的，有关联的ad集合，只对这些相关ad做处理
这步删除了与大量ad关联的账号, bad_accounts.dat
输入：data_file, 所有非家庭ad集合，共享设备
2. 对每个ad对, 对于有指定账号出现，且子图相似的,可合并
   合并：目的是为了给账号a，通过其相关账户b，增加b所在ad的设备。所以往子图里添加帐号就行了。
   输入：上一步的私有设备结果，要处理的关联ad
   输出：添加了账号的私有设备结果

#### generate_output.py
1. 给public设备找账号
2. 输出不跨ad的结果
3. 输出跨ad的结果






