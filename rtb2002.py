#!/usr/bin/env python3

import pyvisa
import time


############################################################
#  Class for work with Rhode&Schwarz oscilloscope RTB2002
############################################################
class oscillograph(object):

    #####################################################################
    #  Init function (trying open VISA TCP Socket)
    #####################################################################
    def __init__(self):

        default_ipaddress = '192.168.1.106'

        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource('TCPIP::'+default_ipaddress+'::INSTR')
        self.inst.close()


    #####################################################################
    # Create connection
    #####################################################################
    def connect(self, ipaddress):

        # Trying to open TCP connection 
        try:
            self.rm = pyvisa.ResourceManager()
            self.inst = self.rm.open_resource('TCPIP::'+ipaddress+'::INSTR')
            print("INFO: Connected oscilloscope with TCP-IP connection:{0}\n\r".format(ipaddress))
            return self.inst
        except: 
            print("ERROR: Can not open connection with IP-address {0}".format(ipaddress))



    #####################################################################
    # Check is device online
    #####################################################################    
    def pingDevice(self, session):
        
        answer = session.query('*IDN?')

        if 'Rohde&Schwarz,RTB2002' in answer:
            print("INFO: Oscilloscope connected ")
            print("Версия ПО: {0}".format(answer))
            return 0
        else:
            print("ERROR: Oscilloscope not found!\n\r")
            return 1


    #####################################################################
    # Reset settings
    ##################################################################### 
    def resetDevice(self, session):

        print("INFO: Reset oscilloscope settings \n\r")
        session.write('*RST')


    #####################################################################
    # Get OPC value 
    #####################################################################
    def getOPC(self, session):

        print("INFO: Getting OPC bit\n\r")

        answer = session.query('*OPC?')

        print("INFO: OPC bit value:"+str(answer)+"\n\r")

        return answer


    #####################################################################
    # Clear status
    #####################################################################
    def clearStatus(self, session):
        
        print("INFO: Clear status \n\r")
        session.write('*CLS')


    #####################################################################
    # Get screenshot from device
    #####################################################################
    def getScreenshot(self, session, screen_name):

        try:

            session.write("MMEM:CDIR '/USB_FRONT/'\n")

            session.write("MMEM:DEL 'SCREEN.png'")
            
            self.getOPC(session)
            self.clearStatus(session)

            session.write("HCOP:LANG PNG;:MMEM:NAME 'SCREEN'")

            session.write("HCOP:IMM\n")

            self.getOPC(session)

            session.values_format.is_binary = True
            session.values_format.datatype = 'B'
            session.values_format.is_big_endian = False
            session.values_format.container = bytearray

            img = session.query_values("MMEM:DATA? 'SCREEN.png'")

            target = open(screen_name, 'wb')
            target.write(img)

            print("INFO: Getting screenshot from device: "+screen_name)
            target.close()

        except:
            print("ERROR: Failed getting screenshot dfrom device")



    ########################################################################################
    #                                                                                      #
    #               Functions for measurments setup                                        #
    #                                                                                      #
    ########################################################################################

    #####################################################################
    #   Set vertical scale
    #   Channel:
    #   - from 1 to 4
    #   Value:
    #   - value in V
    #####################################################################
    def setVertical(self, session, channel, value):
        
        print("INFO: Set vertical scale to channel: "+str(channel)+" value:"+str(value))
        session.write('CHAN'+str(channel)+':SCAL '+str(value))


    #####################################################################
    # Set bandwidth 
    #  'B20' -  20MHz band
    #  'FULL' - full bandwidth
    #####################################################################
    def setBandwidth(self, session, channel, bandwidth):
        
        if bandwidth == '20':
            bandwidth = 'B20'
        else:
            bandwidth = 'FULL'

        print("INFO: Set bandwidth to channel: "+str(channel)+" value:"+str(bandwidth))
        session.write('CHAN'+str(channel)+':BAND '+str(bandwidth))

    
    #####################################################################
    # Set time scale
    # Value:
    # - seconds
    #####################################################################
    def setHorizontal(self, session, value):

        session.write('TIM:SCAL '+str(value))



    ########################################################################################
    #                                                                                      #
    #               Functions for work with oscilloscope channels                          #
    #                                                                                      #
    ########################################################################################

    #####################################################################
    # Set channel state
    # - channel - number of channel
    # - state - 1 - on
    #         - 0 - off
    #####################################################################
    def setChannelState(self, session, channel, state):

        if((state == 1) & (channel == 1)):
            state = 'CHAN1:STAT ON'
        elif((state == 0) & (channel == 1)):
            state = 'CHAN1:STAT OFF'

        if((state == 1) & (channel == 2)):
            state = 'CHAN2:STAT ON'
        elif((state == 0) & (channel == 21)):
            state = 'CHAN2:STAT OFF'

        if((state == 1) & (channel == 3)):
            state = 'CHAN3:STAT ON'
        elif((state == 0) & (channel == 3)):
            state = 'CHAN3:STAT OFF'

        if((state == 1) & (channel == 4)):
            state = 'CHAN4:STAT ON'
        elif((state == 0) & (channel == 4)):
            state = 'CHAN4:STAT OFF'

        session.write(state)


    #####################################################################
    # Set coupling mode on channel on oscilloscope
    #####################################################################
    def setChannelCoupling(self, session, channel, coupling):

        if coupling == 'DC':
            coupling = 'DCL'

        elif coupling == 'AC':
            coupling = 'ACL'

        else:
            coupling = 'GND'

        session.write('CHAN'+str(channel)+':COUP '+str(coupling))


    ########################################################################################
    #                                                                                      #
    #               Functions to work with trigger options                                 #
    #                                                                                      #
    ########################################################################################

    #####################################################################
    # Set trigger source 
    #####################################################################
    def setTriggerSource(self, session, channel):

        if channel == 1:
            channel = 'CH1'

        elif channel == 2:
            channel = 'CH2'

        elif channel == 3:
            channel = 'CH3'

        elif channel == 4:
            channel = 'CH4'

        session.write('TRIG:A:SOUR '+str(channel))


    #####################################################################
    # Function to find trigger level
    #####################################################################
    def setTriggerFindLevel(self, session):

        session.write('TRIG:A:FIND')



    ########################################################################################
    #                                                                                      #
    #               Functions to work with integrated digial voltmeter                     #
    #                                                                                      #
    ########################################################################################

    #####################################################################
    # On/off digital voltmeter
    #####################################################################
    def setVoltmeterState(self, session, state):
        
        if(state == 1):
            state = 'DVM:ENAB ON'
        else:
            state = 'DVM:ENAB OFF'

        session.write(state)


    #####################################################################
    # Set parameters of digital voltmeter
    # Channel:
    # - from 1 to 4
    # Voltage_type:
    # - DC
    # - ACDCrms
    # - ACRMs
    # - OFF
    #####################################################################
    def setVoltmeterParam(self, session, channel, voltage_type):

        if(channel == 1):
            channel = 'DVM:SOUR CH1'

        elif(channel == 2):
            channel = 'DVM:SOUR CH2'

        elif(channel == 3):
            channel = 'DVM:SOUR CH3'

        elif(channel == 4):
            channel = 'DVM:SOUR CH5'

        session.write(channel)


        if(voltage_type == 'DC'):
            voltage_type = 'DVM:TYPE DC'

        elif(voltage_type == 'ACDCrms'):
            voltage_type = 'DVM:TYPE ACDC'

        elif(voltage_type == 'ACRMs'):
            voltage_type = 'DVM:TYPE ACRM'

        elif(voltage_type == 'OFF'):
            voltage_type = 'DVM:TYPE OFF'    

        session.write(voltage_type)


    #####################################################################
    # Function returns voltmeter status
    #####################################################################
    def getVoltmeterStatus(self, session):

        status = session.query('DVM:RES:STAT?')
        status_arr = status.split(',')

        return status_arr[1].replace('\\n\'','')


    #####################################################################
    # Function used for print voltmeter status
    #####################################################################
    def printVoltmeterStatus(self, session):

        state_bin = int(self.getVoltmeterStatus(session))

        if((state_bin & 0x1 ) == 1):
            print ("Result is valid")
        elif((state_bin & 0x1 ) == 0):
            print ("Result is invalid")


        if((state_bin & 0x2 ) == 2):
            print ("No result avaliable")
        elif((state_bin & 0x2 ) == 0):
            print ("Result is avaliable")


        if((state_bin & 0x4 ) == 4):
            print ("No period found")       
        elif((state_bin & 0x4 ) == 0):
            print ("Period found")          


        if((state_bin & 0x8 ) == 8):
            print ("Clipping occurs")      
        elif((state_bin & 0x8 ) == 0):
            print ("Clipping no occurs")    
        

    #####################################################################
    # Get clipping status of digital voltmeter
    #####################################################################    
    def getVoltmeterStatusClipping(self, session):

        state_bin = int(self.getVoltmeterStatus(session))

        if((state_bin & 0x8 ) == 8):
            return 1    
        elif((state_bin & 0x8 ) == 0):
            return 0


    #####################################################################
    # Get voltmeter measured value
    #####################################################################
    def getVoltmeterValue(self, session, channel):

        clipping = self.getVoltmeterStatusClipping(session)

        set_voltage = 0.5

        while clipping == 1:

            set_voltage = set_voltage + 0.5

            self.setVertical(session, channel, set_voltage)

            clipping = self.getVoltmeterStatusClipping(session)

            if(set_voltage > 50):
                exit
        
        time.sleep(3)

        voltage = session.query('DVM:RES?')
        
        voltage = voltage.replace('b\'','').replace('\\n','').replace('\'','')
        
        voltage = round(float(voltage),3)

        return voltage
        

    #####################################################################
    # Print measured value
    #####################################################################
    def printVoltmeterValue(self, session, channel):

        print(self.getVoltmeterValue(session, channel))



    ########################################################################################
    #                                                                                      #
    #               Fuction to work with measure sequence                                  #
    #                                                                                      #
    ########################################################################################

    #####################################################################
    # Set single shot or continous mode measure
    #####################################################################
    def setAcqState(self, session, state):

        if(state == "RUN"):
            nstate = 'RUNC'
        elif(state == "SINGLE"):
            nstate = 'RUNS'

        session.write(nstate)


    ########################################################################################
    #                                                                                      #
    #               Fuction to work with quick measure sequence                            #
    #                                                                                      #
    ########################################################################################

    #####################################################################
    # On/off quick measure mode 
    #####################################################################
    def setQuickMeasState(self, session, state):

        if(state == 1):
            state = 'MEAS:AON'
        else:
            state = 'MEAS:AOFF'

        session.write(state)

    #####################################################################
    # Get quick measure Vpp value
    #####################################################################
    def getQuickMeasVpp(self, session):

        result = session.query('MEAS:ARES?')
        result_arr = result.split(',')
        result_alg = float(result_arr[0])

        return round(result_alg*1000, 1)

    
    #####################################################################
    # Get VULpe value
    #####################################################################
    def getQuickMeasVULpe(self, session):

        result_ul = []

        result = session.query('MEAS:ARES?')

        result_arr = result.split(',')
        result_upe = float(result_arr[1])
        result_lpe = float(result_arr[2])

        result_ul.append(round(result_upe, 1))
        result_ul.append(round(result_lpe, 1))

        return result_ul


    ########################################################################################
    #                                                                                      #
    #               Function uses to get measured values                                   #
    #                                                                                      #
    ########################################################################################


    #####################################################################
    # Get voltage function
    #####################################################################
    def getVoltage(self, session, channel):

        self.resetDevice(session)

        self.setChannelState(session, channel, 1)
        self.setChannelCoupling(session, channel, 'DC')

        self.setVoltmeterState(session, 1)
        self.setVoltmeterParam(session, 1, 'DC')

        return round(self.getVoltmeterValue(session, channel), 1)

    
    #####################################################################
    # Get voltage Peak-to-peak 
    #####################################################################
    def getVoltagePP(self, session, channel, bandwidth, htime):

        voltage = 0.010

        self.resetDevice(session)

        self.setChannelState(session, channel, 1)
        self.setChannelCoupling(session, channel, 'AC')

        self.setVertical(session, channel, voltage)
        self.setHorizontal(session, htime)
        self.setBandwidth(session, channel, bandwidth)
        self.setQuickMeasState(session, 1)

        time.sleep(10)

        self.setTriggerFindLevel(session)

        print("INFO: Searching maximum Vpp in 50 cycles...")

        i = 1
        vpp_result = 0
        vpp_clipping = 0

        while i < 50:

            self.setAcqState(session, "SINGLE")

            time.sleep(1)

            vpp = self.getQuickMeasVpp(session)

            print("DEBUG: VPP = "+str(vpp))

            if (vpp == 9.91e+40) | (vpp < 0) :
                print("DEBUG: (vpp == 9.91e+40) | (vpp < 0) ")

                vpp_clipping = vpp_clipping + 1 
                print("DEBUG: VPP Clipping counter:"+str(vpp_clipping))

                if(vpp_clipping > 10):

                    print("DEBUG: VPP Clipping counter > 10 ")

                    if voltage == 0.010:
                        voltage = 0.020
                    elif voltage == 0.020:
                        voltage = 0.050
                    elif voltage == 0.050:
                        voltage = 0.1
                    elif voltage == 0.1:
                        voltage = 0.2
                    elif voltage == 0.2:
                        voltage = 0.5
                    elif voltage == 0.5:
                        voltage = 1
                    elif voltage == 1:
                        voltage = 2
                    elif voltage == 2:
                        voltage = 5
                    elif voltage == 5:
                        voltage = 10
                    elif voltage == 10:
                        voltage = 20
                    elif voltage == 20:
                        print("ERROR: Maximum voltage, error...")
                        exit()

                    self.setVertical(session, channel, voltage)
                    vpp_clipping = 0

                    print("VPP cliping counter overloaded ")
                    print("INFO/ERROR: set new voltage scale to oscilloscope: "+str(voltage))
                    i = 0
                
                vpp = 0

            if vpp > vpp_result:
                vpp_result = vpp
            
            i = i + 1

        return vpp_result

    
    #####################################################################
    # Fucntion to get VULpe value 
    #####################################################################
    def getVoltageDC(self, session, channel, bandwidth, htime, voltage):

        self.resetDevice(session)

        self.setChannelState(session, channel, 1)
        self.setChannelCoupling(session, channel, 'DC')

        self.setVertical(session, channel, voltage)
        self.setHorizontal(session, htime)
        self.setBandwidth(session, channel, bandwidth)
        self.setQuickMeasState(session, 1)

        time.sleep(10)
        self.setTriggerFindLevel(session)
        
        return self.getQuickMeasVULpe(session)



