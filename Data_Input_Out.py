import Class_Cell as cc
import pandas
import numpy
from copy import deepcopy
from scipy.spatial import Delaunay
import os

def get_neighborSite_by_layerNum(SiteIndexList,Delaunay_SiteAddr,layerNum,ArroundSiteList,ArroundSiteIndexDict,current_layer = 1):
    while current_layer <= layerNum:
        for each in SiteIndexList:
            # 获取三角剖分中一个点的周边相邻点方法：
            # Delaunay.vertex_neighbor_vertice属性获取两个ndarray元组：（indices，indptr）。
            # 顶点k的相邻顶点的索引是 indptr [indices [k]：indices [k + 1]]
            SiteIndexGroup,neighborIndexGroup = Delaunay_SiteAddr.vertex_neighbor_vertices
            neighborIndexList = neighborIndexGroup[SiteIndexGroup[each]:SiteIndexGroup[each+1]]
            for eachNeighIndex in neighborIndexList:
                if eachNeighIndex not in ArroundSiteList:
                    ArroundSiteList.append(eachNeighIndex)
                    ArroundSiteIndexDict[current_layer].append(eachNeighIndex)
        current_layer += 1
        get_neighborSite_by_layerNum(SiteIndexList = neighborIndexList,
                                         Delaunay_SiteAddr = Delaunay_SiteAddr,
                                         layerNum = layerNum,
                                         ArroundSiteList = ArroundSiteList,
                                         ArroundSiteIndexDict = ArroundSiteIndexDict,
                                         current_layer = current_layer)

    return ArroundSiteList,ArroundSiteIndexDict


def validate_projectParameter(table_paras):
    try:
        table_paras['BSCID'] = table_paras['BSCID'].astype('int32')
    except ValueError:
        return 'There are ValueError in "BSCID" Column. Data Type Should Be "int". Please check.'

    try:
        table_paras['SiteID'] = table_paras['SiteID'].astype('int32')
    except ValueError:
        return 'There are ValueError in "SiteID" Column. Data Type Should Be "int". Please check.'

    try:
        table_paras['CellID'] = table_paras['CellID'].astype('int32')
    except ValueError:
        return 'There are ValueError in "CellID" Column. Data Type Should Be "int". Please check.'

    try:
        table_paras['CI'] = table_paras['CI'].astype('int32')
    except ValueError:
        return 'There are ValueError in "CI" Column. Data Type Should Be "int". Please check.'

    try:
        table_paras['LAC'] = table_paras['LAC'].astype('int32')
    except ValueError:
        return 'There are ValueError in "LAC" Column. Data Type Should Be "int". Please check.'

    try:
        table_paras['BSIC'] = table_paras['BSIC'].astype('int8')
    except ValueError:
        return 'There are ValueError in "BSIC" Column. Data Type Should Be "int". Please check.'

    try:
        table_paras['BCCH'] = table_paras['BCCH'].astype('int16')
    except ValueError:
        return 'There are ValueError in "BCCH" Column. Data Type Should Be "int". Please check.'

    try:
        table_paras['longitude'] = table_paras['longitude'].astype('float64')
    except ValueError:
        return 'There are ValueError in "longitude" Column. Data Type Should Be "float". Please check.'

    try:
        table_paras['Latitude'] = table_paras['Latitude'].astype('float64')
    except ValueError:
        return 'There are ValueError in "Latitude" Column. Data Type Should Be "float". Please check.'

    try:
        table_paras['Antenna Azimuth'] = table_paras['Antenna Azimuth'].astype(
            'float16')
    except ValueError:
        return 'There are ValueError in "Antenna Azimuth" Column. Data Type Should Be "int" or "float". Please check.'

    # for each in range(min(500, len(table_paras))):
    #     FreqList = str(table_paras.loc[each, 'TCH']) + \
    #         str(table_paras.loc[each, 'MA'])
    #     if ',' in FreqList:
    #         return 'In TCH/MA_List Column, Separator Between Freqs Should Be ";", but not ",".'

    return 'Data Type Modified.'


"""******************************************************************************************************************************"""
"""从Excel文件中读取数据并格式化函数"""
def read_CellInfo(filename, layerNum,expansion_dict,avail_freq_int_list):  # 从Excel读取所有站点信息
    dict_cell = {}  # 总的小区集合[字典格式,小区序号：小区实例]，序号为Excel中小区所在行数-1
    expansion_indexlist = []
    table_paras = pandas.read_excel(io=filename, sheet_name='Sheet1')
    table_paras.fillna('', inplace=True)
    # print(table_paras['MA_list'])
    output_dir = os.path.split(filename)[0]
    # 检查工参中数据类型
    check_result = validate_projectParameter(table_paras)
    # print(check_result)
    if check_result == 'Data Type Modified.':
        table_paras_indexList = table_paras.index.tolist()
        index = 0
        for index in table_paras_indexList:
            BSCID = int(table_paras.loc[index, 'BSCID'])
            SiteID = int(table_paras.loc[index, 'SiteID'])
            CellID = int(table_paras.loc[index, 'CellID'])

            CI = int(table_paras.loc[index, 'CI'])
            BTS_name = str(table_paras.loc[index, 'SiteName'])
            Cell_name = str(table_paras.loc[index, 'CellName'])
            LAC = int(table_paras.loc[index, 'LAC'])
            BSIC = int(table_paras.loc[index, 'BSIC'])
            BCCH = int(table_paras.loc[index, 'BCCH'])
            Long = float(table_paras.loc[index, 'longitude'])
            Lat = float(table_paras.loc[index, 'Latitude'])
            Antenna_azimuth = int(
                float(table_paras.loc[index, 'Antenna Azimuth']))

            # 如果检查项不涉及TCH或MAlist,则不读入TCH信息，节省内存

            TCH_list = str(table_paras.loc[index, 'TCH'])
            MA_list = str(table_paras.loc[index, 'MA'])



            a = cc.Cell(  # 类实例化，传入各个参数，生成这些实例
                BSCID=BSCID,
                SiteID=SiteID,
                CellID=CellID,
                CI=CI,
                BTS_name=BTS_name,
                Cell_name=Cell_name,
                LAC=LAC,
                BSIC=BSIC,
                BCCH=BCCH,
                TCH_list=TCH_list,
                MA_list=MA_list,
                Long=Long,
                Lat=Lat,
                Antenna_azimuth=Antenna_azimuth,
                index=index,
                avail_freq_list = deepcopy(avail_freq_int_list),
                output_dir = output_dir
            )
            dict_cell[index] = a  # 实例化对象赋予小区字典中对应的小区序号,小区序号为Excel中小区所在行数-1
            cellindex = '_'.join([str(table_paras.loc[index, 'BSCID']),
                              str(table_paras.loc[index, 'SiteID']),
                              str(table_paras.loc[index, 'CellID'])])
            if cellindex in expansion_dict:
                expansion_indexlist.append(index)
                dict_cell[index].setAddedTrxNum(expansion_dict[cellindex])

            index += 1


        # print(len(dict_cell)) #测试用

        # 生成{(经度，纬度):[此经纬度上的小区编号列表]}列表
        dict_SiteAddr_to_Cell = {}  # 字典的键必须是可hash的，列表不可hash，tuple是可hash的
        for i in range(index):
            if (dict_cell[i].Long,
                    dict_cell[i].Lat) not in dict_SiteAddr_to_Cell:  # 向{(经纬度):[小区列表]}字典中添加小区
                dict_SiteAddr_to_Cell[(dict_cell[i].Long, dict_cell[i].Lat)] = [
                    i]
            else:
                dict_SiteAddr_to_Cell[(
                    dict_cell[i].Long, dict_cell[i].Lat)].append(i)

        # 获取共站小区列表
        for each_siteAddr in dict_SiteAddr_to_Cell:
            for each_cellIndex in dict_SiteAddr_to_Cell[each_siteAddr]:
                dict_cell[each_cellIndex].get_CoSite_CellList(
                    dict_SiteAddr_to_Cell[each_siteAddr][:])

        # 获取指定层内的站点信息
        dict_SiteAddr_to_Cell_keys = list(dict_SiteAddr_to_Cell.keys())
        matrix_SiteAddr = [list(x) for x in dict_SiteAddr_to_Cell_keys]
        Delaunay_SiteAddr = Delaunay(numpy.array(matrix_SiteAddr))

        for eachIndex, each_siteAddr in enumerate(dict_SiteAddr_to_Cell_keys):
            ArroundSiteIndexList = []
            ArroundSiteIndexDict = {}
            for i in range(layerNum):
                ArroundSiteIndexDict[i+1] = []
            current_layer = 1
            ArroundSiteIndexList,ArroundSiteIndexDict = get_neighborSite_by_layerNum(SiteIndexList = [eachIndex],
                                                             Delaunay_SiteAddr = Delaunay_SiteAddr,
                                                             layerNum = layerNum,
                                                             ArroundSiteList = ArroundSiteIndexList,
                                                             ArroundSiteIndexDict = ArroundSiteIndexDict,
                                                             current_layer = current_layer)

            ArroundSiteAddrDict = {x:[dict_SiteAddr_to_Cell_keys[y] for y in ArroundSiteIndexDict[x]] for x in ArroundSiteIndexDict}
            ArroundSiteAddrList = [dict_SiteAddr_to_Cell_keys[x] for x in ArroundSiteIndexList]
            # print(ArroundSiteAddrDict)
            # print(ArroundSiteAddrList)
            for eachcell_onSite in dict_SiteAddr_to_Cell[each_siteAddr]:
                dict_cell[eachcell_onSite].getArroundSiteCellList(ArroundSiteAddrList)
                dict_cell[eachcell_onSite].getArroundSiteCellDict(ArroundSiteAddrDict)
                dict_cell[eachcell_onSite].get_polygen_points()
                # 计算小区的覆盖区域的坐标点序列

        del table_paras
        return True, dict_cell, dict_SiteAddr_to_Cell, check_result, expansion_indexlist
    else:
        del table_paras
        return False, None, None, check_result, None


def readExpansionCellInfo(filename_expantion):
    DataFrame = pandas.read_excel(filename_expantion,sheet_name='Cell_Infor')
    expansion_dict = {}
    for each in DataFrame.index.tolist():
        index = '_'.join([str(DataFrame.loc[each,'BSCID']),
                          str(DataFrame.loc[each,'SiteID']),
                          str(DataFrame.loc[each,'CellID'])])
        expansion_dict[index] = int(DataFrame.loc[each,'TRX_num'])
    return expansion_dict













