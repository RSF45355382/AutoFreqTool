import openpyxl
import Data_Input_Out as ds
import wx
import os

'''
设定判断角度对打的条件, 距离和角度
'''
ANGLE_CHECK = [150,75,45]#[180,90,45]
DIS_CHECK = [200,1000,10000]
K_Angle = (ANGLE_CHECK[2] - ANGLE_CHECK[1])/(DIS_CHECK[2] - DIS_CHECK[1])
B_Angle = ANGLE_CHECK[1] - K_Angle*DIS_CHECK[1]
CHECK_LAYER_NUM = 3
POLYG_DIST4ANGLE_LIST = [(-75,0.2),(-60,0.4),(-45,0.6),(-32.5,1),(-17,1.2),(0,1.3),(17,1.2),(32.5,1),(45,0.6),(60,0.4),(75,0.2)]
# print(K_Angle,B_Angle)

# AVAIL_FREQ_LIST = [812,813,814,815,816,817,818,819,820,821,822,823,
#                    824,825,826,827,828,829,830,831,832,833,834,835,
#                    836,837,838,839,840,841,842,843,844,845,846,847,
#                    848,849,850,851,852,853,854,855,856,857,858,859,
#                    860]


class BackGround(wx.Panel):

    def __init__(self, parent):

        self.path_SiteDB = ''
        self.path_ExpansionConfigSettings = ''

        wx.Panel.__init__(self, parent=parent)

        self.filepath_SiteDB_Label = wx.StaticText(self,
                                                        label='*',
                                                        pos=(20, 30),
                                                        size=(10, 10))

        self.filepath_SiteDB_Label = wx.StaticText(self,
                                                        label='*',
                                                        pos=(20, 90),
                                                        size=(10, 10))

        self.filepath_SiteDB_Label = wx.StaticText(
            self, label='Select Site DB File:', pos=(
                30, 30), size=(
                150, 30))

        self.filepath_seprator1_Label = wx.StaticText(
            self,
            label='-------------------------------------------------------------------------',
            pos=(
                30,
                65),
            size=(
                400,
                30))

        self.filepath_ExpansionConfigSettings_Label = wx.StaticText(
            self, label='Select Expansion File:', pos=(
                30, 90), size=(
                150, 30))

        self.filepath_seprator2_Label = wx.StaticText(
            self,
            label='-------------------------------------------------------------------------',
            pos=(
                30,
                130),
            size=(
                400,
                30))

        self.filepath_SiteDB_text = wx.TextCtrl(
            self, value='Site/Cell Database File', pos=(
                180, 30), size=(
                150, 30), style=wx.TE_READONLY)
        self.filepath_ExpansionConfigSettings_text = wx.TextCtrl(
            self, value='Expansion Config File', pos=(
                180, 100), size=(
                150, 30), style=wx.TE_READONLY)
        self.filepath_SiteDB_button = wx.Button(self,
                                                     label='Select File',
                                                     pos=(330, 30),
                                                     size=(70, 30),
                                                     style=wx.EXPAND)
        self.Bind(
            wx.EVT_BUTTON,
            self.select_QuickConfig,
            self.filepath_SiteDB_button)

        self.filepath_ExpansionConfigSettings_button = wx.Button(self,
                                                           label='Select File',
                                                           pos=(330, 100),
                                                           size=(70, 30),
                                                           style=wx.EXPAND)
        self.Bind(
            wx.EVT_BUTTON,
            self.select_TrxConfigSettings,
            self.filepath_ExpansionConfigSettings_button)

        img_file = r'.\res\button.png'
        img = wx.Image(img_file, wx.BITMAP_TYPE_ANY)
        img.Scale(400, 70)
        img_bit = img.ConvertToBitmap()
        self.run_Button = wx.BitmapButton(self,
                                          id=-1,
                                          bitmap=img_bit,
                                          pos=(20, 160),
                                          size=(385, 60),
                                          style=wx.SHAPED)
        self.Bind(wx.EVT_BUTTON, self.main_Program, self.run_Button)

        self.process_text = wx.TextCtrl(
            self, value='Input available Freq List here("1,2,3,4,5")\nPlease cover this part! \n', pos=(
                20, 220), size=(
                385, 100), style=wx.TE_MULTILINE)

    def select_QuickConfig(self, event):
        dlg = wx.FileDialog(
            self, message='Please Select Site/Cell Database File:')
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirpath = dlg.GetDirectory()
            self.path_SiteDB = os.path.join(dirpath, filename)
            self.filepath_SiteDB_text.SetValue(self.path_SiteDB)

    def select_TrxConfigSettings(self, event):
        dlg = wx.FileDialog(
            self, message='Please Select Expansion Config File File:')
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirpath = dlg.GetDirectory()
            self.path_ExpansionConfigSettings = os.path.join(dirpath, filename)
            self.filepath_ExpansionConfigSettings_text.SetValue(
                self.path_ExpansionConfigSettings)

    def main_Program(self, event):
        self.func_status = ''
        if self.path_ExpansionConfigSettings != '' and self.path_SiteDB != '':
            # self.process_text.Clear()
            self.avail_freq_str = self.process_text.GetValue()
            self.process_text.AppendText('\nTool is running...\n')
            self.run_Button.Disable()
            main_func = main_fn(
                self.path_SiteDB,
                self.path_ExpansionConfigSettings,
                self.avail_freq_str
                )
            while True:
                try:
                    self.func_status = next(main_func)
                    self.process_text.AppendText(self.func_status)
                except StopIteration:
                    break
            self.run_Button.Enable()
            self.filepath_SiteDB_text.Clear()
            self.filepath_ExpansionConfigSettings_text.Clear()
            if self.func_status == 'Frequency estimation finished.\n':
                wx.MessageBox(
                    message='The Freq Estimating Result have been saved in the same directory with Expansion File.',
                    style=wx.CENTER)
            else:
                wx.MessageBox(
                    message='File Error, Please check input file.',
                    style=wx.CENTER)
        else:
            if self.path_ExpansionConfigSettings == '':
                self.func_status += 'Expansion File is not selected.\n'
            if self.path_SiteDB == '':
                self.func_status += 'Site DB File is not selected.\n'
            self.process_text.AppendText(self.func_status)


def addTRX(dict_cell,dict_SiteAddr_to_Cell, distance, expansion_indexlist,output_filename):
    len_dict = len(dict_cell)
    i = 0
    expansioncell_num = len(expansion_indexlist)
    for each in expansion_indexlist:
        dict_cell[each].expandTrx(dict_SiteAddr_to_Cell,distance,dict_cell)
        i+=1
        if i%5 == 0 or i == expansioncell_num:
            print('{}/{} cells expanded.'.format(i,expansioncell_num))
    templateWB = openpyxl.load_workbook(r".\res\template\Template.xlsx")
    template = templateWB['Sheet1']
    for each in expansion_indexlist:
        if dict_cell[each].addedTrxNum:
            for each_freq in dict_cell[each].addedFreq:
                freq = each_freq[0][0]
                score = each_freq[0][1]
                detailed = each_freq[1]
                template.append([
                    dict_cell[each].BSCID,
                    dict_cell[each].SiteID,
                    dict_cell[each].CellID,
                    dict_cell[each].Cell_name,
                    dict_cell[each].neededTrxNum,
                    dict_cell[each].addedTrxNum,
                    freq,
                    score,
                    str(detailed),
                    str(dict_cell[each].freqscore_list)
                ])
        else:
            template.append([
                dict_cell[each].BSCID,
                dict_cell[each].SiteID,
                dict_cell[each].CellID,
                dict_cell[each].Cell_name,
                dict_cell[each].neededTrxNum,
                dict_cell[each].addedTrxNum,
                '---',
                '---',
                '---',
                str(dict_cell[each].freqscore_list)
            ])
    templateWB.save(output_filename)

def check_avail_freq_str(avail_freq_str):
    avail_freq_str = avail_freq_str.replace(' ','')
    avail_freq_str = avail_freq_str.replace('\n', '')
    avail_freq_str = avail_freq_str.replace('"', '')
    avail_freq_str = avail_freq_str.replace("'", '')
    for each in avail_freq_str:
        if each not in ['0','1','2','3','4','5','6','7','8','9',',',';']:
            return False,avail_freq_str
    avail_freq_str_list = avail_freq_str.split(',') if ',' in avail_freq_str else avail_freq_str.split(';')
    avail_freq_int_list = [int(each) for each in avail_freq_str_list]
    return True,avail_freq_int_list

def main_fn(PP_filename,filename_expantion,avail_freq_str):
    check_distance = 10000
    # PP_filename = r'C:\Users\10225167\Desktop\扩容频点工具材料\Site_DB_2G_CNO_base_ProjectParameter.xlsx'
    # filename_expantion = r'C:\Users\10225167\Desktop\扩容频点工具材料\expansion_cell.xlsx'
    output_filename = '_Freq_Estim'.join(os.path.splitext(filename_expantion))

    _checkflag, avail_freq_int_list = check_avail_freq_str(avail_freq_str)
    try:
        expansion_dict = ds.readExpansionCellInfo(filename_expantion)
        yield ('Finished reading Expansion File.\n')
    except:
        expansion_dict = None
        yield 'Error occured when reading Expansion File.\n'

    if not _checkflag:
        yield 'AVAIL_FREQ_LIST not availiable.\n'
    else:
        if expansion_dict:
            _db_flag, dict_cell, dict_SiteAddr_to_Cell, check_result, expansion_indexlist = ds.read_CellInfo(PP_filename,
                                                                                               layerNum=CHECK_LAYER_NUM,
                                                                                               expansion_dict=expansion_dict,
                                                                                               avail_freq_int_list = avail_freq_int_list)  # 读取所选Excel文件数据
            if not _db_flag:
                yield 'Error occured when reading Site Database.\n'
            else:
                yield('Finished reading Project Parameter File.\n')
                addTRX(dict_cell, dict_SiteAddr_to_Cell, check_distance, expansion_indexlist,output_filename)
                yield 'Frequency estimation finished.\n'


if __name__ == '__main__':
    # check_distance = 10000
    # PP_filename = r'C:\Users\10225167\Desktop\扩容频点工具材料\Site_DB_2G_CNO_base_ProjectParameter.xlsx'
    # filename_expantion = r'C:\Users\10225167\Desktop\扩容频点工具材料\expansion_cell.xlsx'
    # expansion_dict = ds.readExpansionCellInfo(filename_expantion)
    # print('Finished reading Expansion File.')
    # dict_cell, dict_SiteAddr_to_Cell,check_result,expansion_indexlist = ds.read_CellInfo(PP_filename,
    #                                                                                      layerNum = CHECK_LAYER_NUM,
    #                                                                                      expansion_dict = expansion_dict)  # 读取所选Excel文件数据
    # print('Finished reading Project Parameter File.')
    # if dict_cell:
    #     addTRX(dict_cell, dict_SiteAddr_to_Cell, check_distance, expansion_indexlist)
    app = wx.App(False)
    frame_work = wx.Frame(None, title='TRX Config Tool')
    panel_interface = BackGround(frame_work)
    frame_work.SetSize((430, 380))
    frame_work.SetMinSize((430, 380))
    frame_work.SetMaxSize((430, 380))
    DisplaySize = wx.DisplaySize()  # 获取屏幕大小
    frame_work.Move(DisplaySize[0] / 2 - 215, DisplaySize[1] / 2 - 190)
    frame_work.Show()
    app.MainLoop()


