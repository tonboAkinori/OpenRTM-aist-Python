﻿#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @file  InPortSHMProvider.py
# @brief InPortSHMProvider class
# @date  $Date: 2016/01/08 $
# @author Nobuhiko Miyamoto





import OpenRTM_aist
import OpenRTM
import CSP__POA


##
# @if jp
# @class InPortCSPProvider
# @brief InPortCSPProvider クラス
#
# 通信手段に 共有メモリ を利用した入力ポートプロバイダーの実装クラス。
#
#
# @else
# @class InPortCSPProvider
# @brief InPortCSPProvider class
#
#
#
# @endif
#
class InPortCSPProvider(OpenRTM_aist.InPortProvider, CSP__POA.InPortCsp):
    
  """
  """

  ##
  # @if jp
  # @brief コンストラクタ
  #
  # コンストラクタ
  # Interface Typeにはshared_memoryを指定する
  # 共有メモリの空間名はUUIDで作成し、コネクタプロファイルのdataport.shared_memory.addressに保存する
  #
  # self
  #
  # @else
  # @brief Constructor
  #
  # Constructor
  #
  # self
  # @endif
  #
  def __init__(self):
    OpenRTM_aist.InPortProvider.__init__(self)
    self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("CSPOutPort")

    # PortProfile setting
    self.setInterfaceType("csp_channel")
    self._objref = self._this()
    
    
    
    self._buffer = None

    self._profile = None
    self._listeners = None

    orb = OpenRTM_aist.Manager.instance().getORB()
    self._properties.append(OpenRTM_aist.NVUtil.newNV("dataport.corba_cdr.inport_ior",
                                                      orb.object_to_string(self._objref)))
    self._properties.append(OpenRTM_aist.NVUtil.newNV("dataport.corba_cdr.inport_ref",
                                                      self._objref))
    
    return

  ##
  # @if jp
  # @brief デストラクタ
  #
  # デストラクタ
  #
  # @param self
  #
  # @else
  # @brief Destructor
  #
  # Destructor
  #
  # @param self
  #
  # @endif
  #
  def __del__(self):
    return

  ##
  # @if jp
  # @brief 終了処理
  #
  # @else
  # @brief 
  #
  # 
  #
  # @endif
  #
  def exit(self):
    oid = OpenRTM_aist.Manager.instance().getPOA().servant_to_id(self)
    OpenRTM_aist.Manager.instance().getPOA().deactivate_object(oid)
    
  
  # void init(coil::Properties& prop)
  def init(self, prop):
    pass

  def setBuffer(self, buffer):
    self._buffer = buffer
    return

  def setListener(self, info, listeners):
    self._profile = info
    self._listeners = listeners
    return

  def setConnector(self, connector):
    self._connector = connector
    return
  ##
  # @if jp
  # @brief バッファにデータを書き込む
  #
  # データのサイズは共有メモリも先頭8byteから取得する
  # 共有メモリからデータを取り出しバッファに書き込む
  #
  # @param data 書込対象データ
  #
  # @else
  # @brief 
  #
  # 
  #
  # @param data 
  #
  # @endif
  #
  # ::OpenRTM::PortStatus put()
  #  throw (CORBA::SystemException);
  def put(self, data):
    
    try:
      self._rtcout.RTC_PARANOID("InPortCSPProvider.put()")
      
      if not self._connector:
        self.onReceiverError(data)
        return OpenRTM.PORT_ERROR

      self._rtcout.RTC_PARANOID("received data size: %d", len(data))

      self.onReceived(data)

      ret = self._connector.write(data)

      return self.convertReturn(ret, data)

    except:
      self._rtcout.RTC_TRACE(OpenRTM_aist.Logger.print_exception())
      return OpenRTM.UNKNOWN_ERROR


  ##
  # @if jp
  # @brief データ書き込み可能かを確認
  #
  # @param self 
  # @return True：書き込み可能、False：書き込み不可
  # 
  #
  # @else
  # @brief 
  #
  # @param self 
  # @return 
  #
  # @endif
  #
  def is_writable(self):
    self._rtcout.RTC_PARANOID("is_writable()")
    if self._connector:
      return self._connector.isWritable()
    return False

  def notify(self):
    pass



      
  def onBufferWrite(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE].notify(self._profile, data)
    return

  def onBufferFull(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_FULL].notify(self._profile, data)
    return

  def onBufferWriteTimeout(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE_TIMEOUT].notify(self._profile, data)
    return

  def onBufferWriteOverwrite(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_OVERWRITE].notify(self._profile, data)
    return

  def onReceived(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED].notify(self._profile, data)
    return

  def onReceiverFull(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_FULL].notify(self._profile, data)
    return

  def onReceiverTimeout(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_TIMEOUT].notify(self._profile, data)
    return

  def onReceiverError(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_ERROR].notify(self._profile, data)
    return

      
  def convertReturn(self, status, data):
    if status == OpenRTM_aist.BufferStatus.BUFFER_OK:
      self.onBufferWrite(data)
      return OpenRTM.PORT_OK
            
    elif status == OpenRTM_aist.BufferStatus.BUFFER_ERROR:
      self.onReceiverError(data)
      return OpenRTM.PORT_ERROR

    elif status == OpenRTM_aist.BufferStatus.BUFFER_FULL:
      self.onBufferFull(data)
      self.onReceiverFull(data)
      return OpenRTM.BUFFER_FULL

    elif status == OpenRTM_aist.BufferStatus.BUFFER_EMPTY:
      return OpenRTM.BUFFER_EMPTY

    elif status == OpenRTM_aist.BufferStatus.PRECONDITION_NOT_MET:
      self.onReceiverError(data)
      return OpenRTM.PORT_ERROR

    elif status == OpenRTM_aist.BufferStatus.TIMEOUT:
      self.onBufferWriteTimeout(data)
      self.onReceiverTimeout(data)
      return OpenRTM.BUFFER_TIMEOUT

    else:
      self.onReceiverError(data)
      return OpenRTM.UNKNOWN_ERROR
      
      

  

def InPortCSPProviderInit():
  factory = OpenRTM_aist.InPortProviderFactory.instance()
  factory.addFactory("csp_channel",
                     OpenRTM_aist.InPortCSPProvider,
                     OpenRTM_aist.Delete)
