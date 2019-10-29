import math

"""******************************************************************************************************************************"""
"""经纬度计算距离函数"""
def distance_Calc(lon_a, lat_a, lon_b, lat_b):  # 根据经纬度计算距离
    lon_a_rad = (lon_a / 180) * math.pi  # 换算为弧度
    lon_b_rad = (lon_b / 180) * math.pi
    lat_a_rad = (lat_a / 180) * math.pi
    lat_b_rad = (lat_b / 180) * math.pi
    if lon_a == lon_b and lat_a == lat_b:
        dis = 0
    else:
        dis = 6371393 * math.acos((math.sin(lat_a_rad)) * math.sin(lat_b_rad) + math.cos(
            lat_a_rad) * math.cos(lat_b_rad) * math.cos(lon_b_rad - lon_a_rad))  # 经纬度距离计算公式
    return dis


"""******************************************************************************************************************************"""
"""经纬度转墨卡托坐标"""
def lonLat2Mercator(Long, Lat):
    R_EARTH = 6371393
    mer_X = R_EARTH*math.cos(Lat/180*math.pi)*math.cos(Long/180*math.pi)
    mer_Y = R_EARTH*math.cos(Lat/180*math.pi)*math.sin(Long/180*math.pi)

    # x = Long * 20037508.342789 / 180
    # y = math.log(math.tan((90 + Lat) * math.pi / 360)) / (math.pi / 180)
    # y = y * 20037508.34789 / 180
    # return x,y

    # return mer_X,mer_Y

    # 最终发现所有类型的换算都会造成坐标误差, 且误差不小, 所以直接使用原经纬度作为直角坐标, 这样误差小一些
    return Long, Lat

"""******************************************************************************************************************************"""
"""相对角度归一化"""
def ang_to_180(ang):
    ang = - ang + 90  # 角度规整（工参中角度顺时针增长）
    while ang >= 360 or ang < 0:  # 在范围0到360范围外的一直规整到所需范围内
        if ang >= 360:
            ang = ang - 360
        if ang < 0:
            ang = ang + 360
    return ang


# """******************************************************************************************************************************"""
# """小区方位计算——单向相对位置"""
# def SingCell_FaceTo(x_cell_1, y_cell_1, x_cell_2, y_cell_2, dir_cell_1, width):
#     if x_cell_1 == x_cell_2 and y_cell_1 == y_cell_2:  # 经纬度都相同（共站址）的情况下算在范围内
#         return True
#     else:
#         if x_cell_2 != x_cell_1:  # 经度不同的情况下计算相对位置，注意弧度角度换算以及arctan函数的取值范围
#             dir_ang_1to2 = math.atan(
#                 (y_cell_2 - y_cell_1) / (x_cell_2 - x_cell_1))
#             if x_cell_1 > x_cell_2:
#                 oto_dir_ang = abs(
#                     ang_to_180(
#                         dir_ang_1to2 /
#                         math.pi *
#                         180 +
#                         180) -
#                     dir_cell_1)
#             else:
#                 oto_dir_ang = abs(
#                     ang_to_180(
#                         dir_ang_1to2 /
#                         math.pi *
#                         180) -
#                     dir_cell_1)
#         else:
#             if y_cell_1 > y_cell_2:
#                 oto_dir_ang = abs(ang_to_180(-90) - dir_cell_1)
#             else:
#                 oto_dir_ang = abs(ang_to_180(90) - dir_cell_1)
#         if oto_dir_ang <= width:  # 如果相对角度小于等于所规定宽度，则认为在范围内，宽度一般定义为30°（实则表示左右各30°，是60°）
#             # 宽度width可调节
#             return True
#         else:  # 否则认为不在范围内
#             return False


"""******************************************************************************************************************************"""
"""小区方位计算——单向相对位置"""
def SingCell_FaceTo(x_cell_1, y_cell_1, x_cell_2, y_cell_2, dir_cell_1, width):
    if x_cell_1 == x_cell_2 and y_cell_1 == y_cell_2:  # 经纬度都相同（共站址）的情况下算在范围内
        return True
    len_orient_vector = math.sqrt((x_cell_2 - x_cell_1) ** 2 + (y_cell_2 - y_cell_1) ** 2)
    orient_vector = ((x_cell_2 - x_cell_1),(y_cell_2 - y_cell_1))
    print("\t\t"+str(orient_vector))

    azimuth_vector = (math.cos((-dir_cell_1+90)/180*math.pi),math.sin((-dir_cell_1+90)/180*math.pi))
    # print("\t\t",x_cell_1, y_cell_1, x_cell_2, y_cell_2)
    print("\t\t"+str(azimuth_vector))
    print("\t\t" + str(dir_cell_1))

    degree_rad = (orient_vector[0]*azimuth_vector[0]+orient_vector[1]*azimuth_vector[1])/len_orient_vector
    degree = math.acos(degree_rad)/math.pi*180

    if  degree < width:
        print("\t"+str(degree)+'<'+str(width))
        return True
    else:
        print("\t"+str(degree)+'>'+str(width))
        return False


"""******************************************************************************************************************************"""
"""小区方位计算（两个互相对打判断）"""
def DualCell_FaceTo(lon_1, lat_1, lon_2, lat_2,dir_cell_1,dir_cell_2,width):
    print("\t\t", lon_1, lat_1, lon_2, lat_2)
    print(((lon_2 - lon_1), (lat_2 - lat_1)))
    x_cell_1,y_cell_1 = lonLat2Mercator(lon_1, lat_1)
    x_cell_2,y_cell_2 = lonLat2Mercator(lon_2, lat_2)
    print("\t\t", x_cell_1, y_cell_1, x_cell_2, y_cell_2)
    Num_FaceTo = 0
    FaceTo_1to2 = 0  # 是否第一个小区打向第二个小区
    FaceTo_2to1 = 0  # 是否第二个小区打向第一个小区
    if SingCell_FaceTo(
            x_cell_1,
            y_cell_1,
            x_cell_2,
            y_cell_2,
            dir_cell_1,
            width):
        Num_FaceTo += 1
        FaceTo_1to2 = 1

    if SingCell_FaceTo(
            x_cell_2,
            y_cell_2,
            x_cell_1,
            y_cell_1,
            dir_cell_2,
            width):
        Num_FaceTo += 1
        FaceTo_2to1 = 1

    # 根据Num_FaceTo参数的值来判断是否对打或者只是一个小区打另一个小区
    if Num_FaceTo == 2:
        return 'Face To EachOther'
    elif Num_FaceTo == 1:
        if FaceTo_1to2:
            return 'A Face To B'
        if FaceTo_2to1:
            return 'B Face To A'
    else:
        return 'Non Face To'


"""******************************************************************************************************************************"""
"""生成字典{频点:[小区号列表]} option = 0->BCCH  option = 1->TCH"""
# 生成字典{频点:[小区号列表]} option = 0->BCCH  option = 1->TCH
def get_dict_freq_to_CellList(Cell_List, dict_cell, option=0):
    # 暂且核查TCH项，MAList之后再做
    freq_list = []
    dict_freq_to_CellList = {}
    if option == 0:  # 针对BCCH
        for each in Cell_List:  # 获取所有频点
            freq_list.append(dict_cell[each].BCCH)
        freq_set = set(freq_list)  # 获取所有频点的集合
        for each in freq_set:
            dict_freq_to_CellList[each] = []  # 在输出结果字典中为每个频点创建一个键,值为一个空列表
        for each_cell in Cell_List:
            dict_freq_to_CellList[dict_cell[each_cell].BCCH].append(each_cell)
    else:  # 针对TCH
        for each in Cell_List:  # 获取所有频点
            freq_list.extend(dict_cell[each].TCH_list)
        freq_set = set(freq_list)  # 获取所有频点的集合
        for each in freq_set:
            dict_freq_to_CellList[each] = []  # 在输出结果字典中为每个频点创建一个键,值为一个空列表
        for each_cell in Cell_List:
            for each_freq in dict_cell[each_cell].TCH_list:
                dict_freq_to_CellList[each_freq].append(each_cell)
    return dict_freq_to_CellList


"""******************************************************************************************************************************"""
"""筛选选定范围内站点"""
def Site_Filter(Ser_Site_Pos, arroundSiteDict, distance):
    Filted_SiteDict = {}
    radius_earth = 6371393
    radius_on_Lat = radius_earth * \
        math.cos((Ser_Site_Pos[1] / 180) * math.pi)  # 该纬度方向上的纬线半径/粗筛使用的, 已经废弃不用

    for each in arroundSiteDict:  # 由于加入和层的概念, 大大减少了需要检查的小区的数量, 不再进行粗筛和细筛两次, 直接一次搞定
        Filted_SiteDict[each] = []
        for eachpos in arroundSiteDict[each]:
            if distance_Calc(
                    Ser_Site_Pos[0],
                    Ser_Site_Pos[1],
                    eachpos[0],
                    eachpos[1]) <= distance:  # 小于初定距离才被选中
                Filted_SiteDict[each].append(eachpos)
    # print(Filted_SiteDict)
    return Filted_SiteDict


"""******************************************************************************************************************************"""
"""根据方位角计算夹角"""
def calcAngleByAzim(azim1,azim2):
    azim1 = 90 - azim1
    azim2 = 90 - azim2

    x_1,y_1 = math.cos((azim1/ 180) * math.pi),math.sin((azim1/ 180) * math.pi)
    x_2,y_2 = math.cos((azim2/ 180) * math.pi),math.sin((azim2/ 180) * math.pi)

    cos_value = (x_1*x_2 + y_1*y_2)/(math.sqrt(x_1**2+y_1**2)*math.sqrt(x_2**2+y_2**2))
    # print(cos_value)
    if cos_value > 1:
        cos_value = 1
    if cos_value < -1:
        cos_value = -1
    return math.acos(cos_value)


"""******************************************************************************************************************************"""
"""根据小区覆盖的区域polygen的points坐标, 直角坐标"""
def calc_polyg_coor(angle, coef, length):
    return coef*math.cos(angle)*length,coef*math.sin(angle)*length

def calc_polyg_points(x,y,azimuth,length_dist,angle_list):
    azimuth = 90-azimuth
    result_list = [[x+calc_polyg_coor((azimuth+angle)/180*math.pi, coef, length_dist)[0],
                    y+calc_polyg_coor((azimuth+angle)/180*math.pi, coef, length_dist)[1]] for (angle, coef) in angle_list]
    result_list.insert(0,[x,y])
    return result_list

"""******************************************************************************************************************************"""
if __name__ == "__main__":  # 测试用
    #print(distance_Calc(115.680204, 39.863602, 115.663456, 39.859525))
    (mercator_X1, mercator_Y1) = lonLat2Mercator(116.386345, 39.870262)
    (mercator_X2, mercator_Y2) = lonLat2Mercator(116.386345, 39.870265)
    dir_1 = 0
    dir_2 = 180
    a = DualCell_FaceTo(
        mercator_X1,
        mercator_Y1,
        mercator_X2,
        mercator_Y2,
        dir_1,
        dir_2,
        30)
    print(a)
