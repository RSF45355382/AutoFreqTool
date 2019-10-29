"""******************************************************************************************************************************"""
"""定义Cell类"""
from Data_Tidy import (Site_Filter,get_dict_freq_to_CellList,distance_Calc,DualCell_FaceTo,calcAngleByAzim,SingCell_FaceTo,calc_polyg_points)
from statistics import median
from AutoFreqTool import ANGLE_CHECK,DIS_CHECK,K_Angle,B_Angle,POLYG_DIST4ANGLE_LIST
import math,statistics
from shapely.geometry import Polygon,Point
import geopandas as gpd


class Cell():
    # 频率核查需要小区属性：小区名，站名，CI,CellID，SiteID，BSCID，BSIC，BCCH,TCH序列，MAList，经纬度，方位角（缺省方位角的置空），
    EARTH_RADIUS = 6371393  # 地球半径,单位米

    def __init__(
            self,  # 所有参数均是str输入
            BSCID=None,
            SiteID=None,
            CellID=None,
            CI=None,
            BTS_name=None,
            Cell_name=None,
            BSIC=None,
            BCCH=None,
            TCH_list=None,
            MA_list=None,
            Long=None,
            Lat=None,
            Antenna_azimuth=None,
            LAC=None,
            index=None,
            avail_freq_list = None,
            output_dir = None):  # 度数格式
        if len(TCH_list) > 1:
            while TCH_list[-1] == " " or TCH_list[-1] == ";" or TCH_list[-1] == ",":
                TCH_list = TCH_list[:-1]
        if ";" in TCH_list:
            TCH_list = (TCH_list.replace(" ", "")).split(
                ";")  # TCH格式为str，去空格，去逗号以后生成int频点列表
        elif "," in TCH_list:
            TCH_list = (TCH_list.replace(" ", "")).split(
                ",")  # TCH格式
        else:
            TCH_list = [TCH_list]

        if len(MA_list) > 1:
            while MA_list[-1] == " " or MA_list[-1] == ";" or MA_list[-1] == ",":
                MA_list = MA_list[:-1]
        if ";" in MA_list:
            MA_list = ((MA_list.replace(" ", "")).split(
                "/")[0]).split(';')  # MA格式为str，去空格，去逗号以后生成int频点列表
        elif "," in MA_list:
            MA_list = ((MA_list.replace(" ", "")).split(
                "/")[0]).split(',')  # MA格式为str，去空格，去逗号以后生成int频点列表
        else:
            MA_list = MA_list.replace(" ", "").split(
                "/")[0]


        # 初始化赋值小区各个属性
        self.index = index
        self.CI = CI
        self.CellID = CellID
        self.BTS_name = BTS_name
        self.Cell_name = Cell_name
        self.BCCH = [BCCH]  # BCCH也整理成list格式的,与TCH统一
        if TCH_list == [""]:
            self.TCH_list = []
        else:
            self.TCH_list = [int(x) for x in TCH_list]  # List格式

        if MA_list == ['']:  # 如果MAList空，则使用TCH代替
            self.MA_list = []
        else:
            self.MA_list = []
            # self.MA_list = [int(ele) for ele in MA_list]  # List格式

        self.Long = Long
        self.Lat = Lat
        self.x = 6371393*math.cos(self.Lat/180*math.pi)*math.cos(self.Long/180*math.pi)
        self.y = 6371393*math.cos(self.Lat/180*math.pi)*math.sin(self.Long/180*math.pi)
        self.Antenna_azimuth = Antenna_azimuth
        self.LAC = LAC
        self.BSCID = BSCID
        self.SiteID = SiteID
        self.BSIC = BSIC

        if BSIC < 10:  # 计算NCC和BCC
            self.NCC = 0
            self.BCC = int(BSIC)
        else:
            self.NCC = int(BSIC / 10)
            self.BCC = int(BSIC % 10)


        if self.TCH_list == []:
            self.TCH_list = self.MA_list

        self.log_name = output_dir+'\\{}.txt'.format(self.Cell_name)


        self.avail_freq_list = avail_freq_list

        self.dualface2celllist = []
        self.singleface2celllist = []
        self.nonface2celllist = []

        self.arroundSiteList = []
        self.arroundCellList = []

        self.neigh_distance = []
        self.median_distance = 0
        self.freq_score_dict = {}
        self.freqscore_list = []

        self.arroundCellDict = {}
        self.usedarround_freq_dict = {}
        self.usedfreq_score_dict = {}

        self.addedFreq = []
        self.neededTrxNum = 0
        self.addedTrxNum = 0

    def setAddedTrxNum(self,num):
        self.neededTrxNum = num

    # 获取与本小区共站的小区索引列表【列表内为小区索引】
    def get_CoSite_CellList(self,CoSite_CellList):
        self.CoSite_CellList = CoSite_CellList
        self.CoSite_CellList.remove(self.index)

    def getArroundSiteCellList(self,ArroundSiteAddrList):
        if (self.Long,self.Lat) in ArroundSiteAddrList:
            ArroundSiteAddrList.remove((self.Long,self.Lat))
        self.arroundSiteList = ArroundSiteAddrList
        # for each in ArroundSiteAddrList:
        #     self.arroundCellList.extend(dict_SiteAddr_to_Cell[each])

    def getArroundSiteCellDict(self,ArroundSiteAddrDict):
        # 剔除本站在字典中位置(三角剖分有时候会获取到本站的位置)
        for each in ArroundSiteAddrDict:
            if (self.Long, self.Lat) in ArroundSiteAddrDict[each]:
                ArroundSiteAddrDict[each].remove((self.Long, self.Lat))
        self.arroundSiteDict = ArroundSiteAddrDict
        # for each in ArroundSiteAddrDict:
        #     self.arroundCellDict[each] = []
        #     for eachpos in ArroundSiteAddrDict[each]:
        #         self.arroundCellDict[each].extend(dict_SiteAddr_to_Cell[eachpos])

    def calcAvgNeighSiteDist(self):
        # 计算正向方向平均站间距
        calc_avgdist = []
        for each_addr in self.arroundSiteList:
            each_addr_x = 6371393*math.cos(each_addr[1]/180*math.pi)*math.cos(each_addr[0]/180*math.pi)
            each_addr_y = 6371393*math.cos(each_addr[1]/180*math.pi)*math.sin(each_addr[0]/180*math.pi)
            if SingCell_FaceTo(self.x, self.y, each_addr_x, each_addr_y, self.Antenna_azimuth,45):
                dist = distance_Calc(self.Long, self.Lat, each_addr[0], each_addr[1])
                calc_avgdist.append(dist)
        calc_avgdist.sort()
        if len(calc_avgdist) >= 3:
            calc_avg_dis_list = calc_avgdist[:3]
        elif len(calc_avgdist):
            calc_avg_dis_list = calc_avgdist
        else:
            calc_avg_dis_list = [10000]
            # 没有对打小区的时候取10km为覆盖距离
        self.avg_neighsite_dist = statistics.median(calc_avg_dis_list)

    def calc_polygen_points(self):
        # 计算小区覆盖区域polygen点坐标序列
        self.polygen_dist4angle_list = POLYG_DIST4ANGLE_LIST[:]
        self.polyg_points = calc_polyg_points(self.x,self.y,self.Antenna_azimuth,self.avg_neighsite_dist,self.polygen_dist4angle_list)

    def get_polygen_points(self):
        # 获取小区覆盖区域polygen点坐标序列
        self.calcAvgNeighSiteDist()
        self.calc_polygen_points()

    # 获取在本小区限定范围内的非共站小区索引列表【列表内为小区索引】
    def get_Arround_CellList(self,dict_SiteAddr_to_Cell,distance):
        self.Arround_SiteDict = Site_Filter(
            (self.Long,self.Lat),
            self.arroundSiteDict,
            distance)  # 获取主站点周边distance距离范围内的所有站点
        # 获取主站点周边distance距离范围内的所有站点上的所有小区序号
        self.Arround_CellDict = {}
        for each in self.Arround_SiteDict:
            self.Arround_CellDict[each] = []
            for eachpos in self.Arround_SiteDict[each]:
                self.Arround_CellDict[each].extend(dict_SiteAddr_to_Cell[eachpos])

        self.neigh_distance = [distance_Calc(self.Long,self.Lat,y[0],y[1])
                                for x in self.Arround_SiteDict
                               for y in self.Arround_SiteDict[x]]
        # print(self.neigh_distance)
        self.median_distance = median(self.neigh_distance)
        # print(self.median_distance)

        # # 获取限定范围内的小区索引列表【共站加周边】
        # self.FreqCheck_CellList = self.CoSite_CellList + self.Arround_CellList
        # # 获取限定范围内的小区列表的{频点:[小区索引列表]}
        # self.FreqCheck_BCCHFreq2CellDict = get_dict_freq_to_CellList(self.FreqCheck_CellList, dict_cell, option=0)
        # self.FreqCheck_TCHFreq2CellDict = get_dict_freq_to_CellList(self.FreqCheck_CellList, dict_cell, option=1)

    def checkArroundFace2CellFreq(self,dict_cell):
        # 检查周边小区的对打特性
        for eachLayer in self.Arround_CellDict:
            for each in self.Arround_CellDict[eachLayer]:
                self.f.write('\t'+dict_cell[each].Cell_name+'\n')
                print(dict_cell[each].Cell_name)
                # m = dict_cell[each]

                dis = distance_Calc(self.Long, self.Lat, dict_cell[each].Long, dict_cell[each].Lat)
                self.f.write("\t\tDistance: " + str(dis) + '\n')
                print("\t\tDistance: " + str(dis))
                # 不同的距离, 对打判断角度也不同
                # if dict_cell[each].Cell_name == 'DN2897C':
                #     print("\tcell got!!!!!!!!!!!!!!!!!!!!!!!")
                if dis<= DIS_CHECK[0]:
                    angle = ANGLE_CHECK[0]
                elif dis <= DIS_CHECK[1]:
                    angle = ANGLE_CHECK[1]
                elif dis <= DIS_CHECK[2]:
                    angle = K_Angle*dis + B_Angle
                else:
                    angle = ANGLE_CHECK[2]
                self.f.write("\t\tAngle: {:.2f}".format(angle) + '\n')
                face2check_result = DualCell_FaceTo(self.Long,
                                                    self.Lat,
                                                    dict_cell[each].Long,
                                                    dict_cell[each].Lat,
                                                    self.Antenna_azimuth,
                                                    dict_cell[each].Antenna_azimuth,
                                                    angle)
                # print("\t"+face2check_result)
                if face2check_result == "Face To EachOther":
                    self.dualface2celllist.append((each,eachLayer))
                    self.f.write('\t\tput into dualface2celllist' + '\n')
                    print('\t\tput into dualface2celllist')
                elif face2check_result == "Non Face To":
                    self.nonface2celllist.append((each,eachLayer))
                    self.f.write('\t\tput into nonface2celllist' + '\n')
                    print('\t\tput into nonface2celllist')
                else:
                    self.singleface2celllist.append((each,eachLayer))
                    self.f.write('\t\tput into singleface2celllist' + '\n')
                    print('\t\tput into singleface2celllist')

    def removeFreq(self,Freq,cellname):
        self.avail_freq_list.remove(Freq)
        self.f.write('%d Freq deleted due to conflict with cell: %s'%(Freq,cellname) + '\n')
        print('\t%d Freq deleted due to conflict with cell: %s'%(Freq,cellname))


    def removeSelfCellFreq(self):
        # 除去本区的所有已用频点(同邻频)
        freqlist_temp = self.BCCH + self.TCH_list
        for eachfreq in freqlist_temp:
            if eachfreq in self.avail_freq_list:
                self.removeFreq(eachfreq, 'SelfCell')
            if eachfreq + 1 in self.avail_freq_list:
                self.removeFreq(eachfreq+1, 'SelfCell')
            if eachfreq - 1 in self.avail_freq_list:
                self.removeFreq(eachfreq-1, 'SelfCell')

    def removeCoSiteFreq(self,dict_cell):
        # 除去共站的所有小区的所有已用频点(同邻频)
        for each in self.CoSite_CellList:
            freqlist_temp = dict_cell[each].BCCH+dict_cell[each].TCH_list
            # print(self.avail_freq_list)
            for eachfreq in freqlist_temp:
                if eachfreq in self.avail_freq_list:
                    self.removeFreq(eachfreq, dict_cell[each].Cell_name)
                if eachfreq+1 in self.avail_freq_list:
                    self.removeFreq(eachfreq+1, dict_cell[each].Cell_name)
                if eachfreq-1 in self.avail_freq_list:
                    self.removeFreq(eachfreq-1, dict_cell[each].Cell_name)

    def removeDualFace2CellFreq(self,dict_cell):
        # 除去双向对打的所有周边小区的所有已用频点(同邻频)
        for each in self.dualface2celllist:
            freqlist_temp = dict_cell[each[0]].BCCH+dict_cell[each[0]].TCH_list
            for eachfreq in freqlist_temp:
                if int(eachfreq) in self.avail_freq_list:
                    self.removeFreq(eachfreq, dict_cell[each[0]].Cell_name)
                if int(eachfreq)+1 in self.avail_freq_list:
                    self.removeFreq(eachfreq+1, dict_cell[each[0]].Cell_name)
                if int(eachfreq)-1 in self.avail_freq_list:
                    self.removeFreq(eachfreq-1, dict_cell[each[0]].Cell_name)

    def removeNearSingleFace2CellFreq(self,dict_cell):
        # 除去单项对打的距离比较近的已用频点, 距离小于中位数距离的情况下才取出这个站点上的已用频点, 否则保留
        # 仅针对3层以内的小区(仅同频)
        for each_cell in self.singleface2celllist:
            if each_cell[1]<2:
                # print(each_cell[1])
                # distance = distance_Calc(self.Long, self.Lat, dict_cell[each_cell[0]].Long, dict_cell[each_cell[0]].Lat)
                # if distance < self.median_distance:
                # print(dict_cell[each_cell[0]].BCCH)
                freqlist_temp = dict_cell[each_cell[0]].BCCH+dict_cell[each_cell[0]].TCH_list
                # print(freqlist_temp)
                for eachfreq in freqlist_temp:
                    if int(eachfreq) in self.avail_freq_list:
                        self.removeFreq(eachfreq, dict_cell[each_cell[0]].Cell_name)

    def pickFreq(self,dict_cell):
        # 在经过同站频点剔除/对打小区频点剔除/单向对打小区频点突出后, 还有部分频点可用
        # 在剩余频点中选取可用频点, 计算这些频点在周边小区的使用情况
        # 给每一频点计算一个分值, 最后排序这个分数得到采用的频点
        usedarround_freq_dict = {}
        arround_cell_list = self.nonface2celllist + self.singleface2celllist
        # 周边的小区列表
        for each_cell in arround_cell_list:
            freqlist_temp = dict_cell[each_cell[0]].BCCH+dict_cell[each_cell[0]].TCH_list
            for each_freq in freqlist_temp:
                if usedarround_freq_dict.get(each_freq,None):
                    usedarround_freq_dict[each_freq].append(each_cell)
                else:
                    usedarround_freq_dict[each_freq] = [each_cell]
        # 生成{频点:[小区索引]}的字典
        self.usedarround_freq_dict = usedarround_freq_dict

        # 分值字典
        for freq,cell_list in self.usedarround_freq_dict.items():
            len_temp = len(cell_list)
            numerator = 0
            cell_list_temp = []
            for each in cell_list:
                cell_index_temp = each[0]
                cell_layer = each[1]
                dis_temp = distance_Calc(self.Long,self.Lat,dict_cell[cell_index_temp].Long,dict_cell[cell_index_temp].Lat)
                rad = calcAngleByAzim(self.Antenna_azimuth,dict_cell[cell_index_temp].Antenna_azimuth)
                numerator += cell_layer*dis_temp/self.median_distance*rad
                cell_list_temp.append((cell_layer,dis_temp,rad,dict_cell[cell_index_temp].Cell_name))
            score_temp = numerator/(len_temp**2)
            self.usedfreq_score_dict[freq] = (score_temp,cell_list_temp)


        for each_freq in self.avail_freq_list:
            if each_freq in self.usedfreq_score_dict:
                self.freq_score_dict[each_freq] = self.usedfreq_score_dict[each_freq]
            else:
                self.freq_score_dict[each_freq] = (10,[(0,0,0,'')])


        freqscore_list = [(x,self.freq_score_dict[x][0]) for x in list(self.freq_score_dict.keys())]
        if len(freqscore_list):
            freqscore_list.sort(key=lambda x: x[1],reverse = True)
        self.freqscore_list = freqscore_list


        for i in range(len(freqscore_list)):
            if i >= self.neededTrxNum:
                break
            else:
                self.TCH_list.append(freqscore_list[i][0])
                self.addedFreq.append((freqscore_list[i],self.freq_score_dict[freqscore_list[i][0]]))
                self.addedTrxNum += 1

    def expandTrx(self,dict_SiteAddr_to_Cell,distance,dict_cell):
        with open(self.log_name,'w') as self.f:
            self.f.write('Cell Analysis: {}'.format(self.Cell_name) + '\n')
            # 获取周边站点
            self.get_Arround_CellList(dict_SiteAddr_to_Cell,distance)
            # 检查周边站点小区对打性质
            self.checkArroundFace2CellFreq(dict_cell)
            # 剔除本小区的频点(同邻频)
            self.removeSelfCellFreq()
            # 剔除本站其他小区的频点(同邻频)
            self.removeCoSiteFreq(dict_cell)
            # 剔除对打小区的频点(同邻频)
            self.removeDualFace2CellFreq(dict_cell)
            # 剔除单向对打小区的频点(仅同频)
            self.removeNearSingleFace2CellFreq(dict_cell)
            # 获取频点
            self.pickFreq(dict_cell)
        self.f.close()

















