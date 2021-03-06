#!/usr/bin/env python
# -*- coding: euc-jp -*-

##
# @file CSPEventPort.py
# @brief CSPEventPort template class
# @date $Date: $
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2019
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.

import OpenRTM_aist
import OpenRTM_aist.EventPort
import copy
import threading



##
# @if jp
#
# @class CSPEventPort
#
# @brief CSPEventPort テンプレートクラス
# 
#
# @since 2.0.0
#
# @else
#
# @class CSPEventPort
#
# @brief CSPEventPort template class
#
#
# @since 2.0.0
#
# @endif
#
class CSPEventPort(OpenRTM_aist.InPortBase):
  ##
  # @if jp
  #
  # @brief コンストラクタ
  #
  # コンストラクタ。
  # パラメータとして与えられる T 型の変数にバインドされる。
  #
  # @param self
  # @param name EventInPort 名。EventInPortBase:name() により参照される。
  # @param fsm FSM
  #
  # @else
  #
  # @brief A constructor.
  #
  # constructor.
  # This is bound to type-T variable given as a parameter.
  #
  # @param self
  # @param name A name of the EventInPort. This name is referred by
  #             EventInPortBase::name().
  # @param value type-T variable that is bound to this EventInPort.
  # @param fsm 
  #
  # @endif
  #
  def __init__(self, name, fsm=None):
    super(CSPEventPort, self).__init__(name, "any")
    self._ctrl = CSPEventPort.WorkerThreadCtrl()
    self._name = name
    self._value = None

    self._OnRead = None

    self._singlebuffer  = True
    self._eventbuffer = None

    self._channeltimeout = 10
    self._bufferzeromode = False
    self._fsm = fsm
    
    if fsm:
      fsm.addInPort(self)
    self._writingConnector = None


    
    
  ##
  # @if jp
  #
  # @brief デストラクタ
  #
  # デストラクタ。
  #
  # @param self
  #
  # @else
  #
  # @brief Destructor
  #
  # Destructor
  #
  # @param self
  #
  # @endif
  #
  def __del__(self):
    super(CSPEventPort, self).__del__()
    if self._eventbuffer is not None:
      OpenRTM_aist.CdrBufferFactory.instance().deleteObject(self._eventbuffer)


  ##
  # @if jp
  #
  # @brief ポート名称を取得する。
  #
  # ポート名称を取得する。
  #
  # @param self
  # @return ポート名称
  #
  # @else
  #
  # @brief Get port name
  #
  # Get port name.
  #
  # @param self
  # @return The port name
  #
  # @endif
  #
  def name(self):
    return self._name



  ##
  # @if jp
  #
  # @brief 引数なしのイベントハンドラを登録する
  #
  # @param self
  # @param name イベント名
  # @param handler イベントハンドラ
  # コネクタ接続時にfsm_event_nameという要素を設定する。
  # fsm_event_nameとイベント名が一致するとイベントが実行される。
  # イベントハンドラにはMacho等で定義したイベントを入力する
  # 
  #
  # @else
  #
  # @param self
  # @param name 
  # @param handler 
  #
  # @endif
  #
  def bindEvent0(self, name, handler):
    self.addConnectorDataListener(OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED,
                                  OpenRTM_aist.EventPort.EventBinder0(self._fsm, name, handler, self._eventbuffer))
    
  ##
  # @if jp
  #
  # @brief 引数ありのイベントハンドラを登録する
  #
  # @param self
  # @param name イベント名
  # @param handler イベントハンドラ
  # @param data_type 入力データ
  #
  # @else
  #
  # @brief 
  #
  # @param self
  # @param name 
  # @param handler 
  # @param data_type 
  #
  # @endif
  #
  def bindEvent1(self, name, handler, data_type):
    self.addConnectorDataListener(OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED,
                                  OpenRTM_aist.EventPort.EventBinder1(self._fsm, name, handler, data_type, self._eventbuffer))

  ##
  # @if jp
  #
  # @brief 初期化関数
  #
  # @param self
  # @param prop コネクタのプロパティ
  # buffer(dataport.buffer)要素でバッファ長さ等を設定
  # channel_timeout(dataport.channel_timeout)要素で、
  # 送信可能なアウトポートが存在しない場合のブロックのタイムアウトを設定
  # 
  # @return ポート名称
  #
  # @else
  #
  # @brief Get port name
  #
  # @param self
  # @param prop 
  #
  # @endif
  #
  def init(self,prop):
    super(CSPEventPort, self).init(prop)

    num = [10]
    if OpenRTM_aist.stringTo(num, self._properties.getProperty("channel_timeout","10")):
      self._channeltimeout = num[0]

    buff_prop = prop.getNode("buffer")
    length = [8]
    OpenRTM_aist.stringTo(length, buff_prop.getProperty("length","8"))

    if length[0] == 0:
      buff_prop.setProperty("length","1")
      self._bufferzeromode = True

    self._eventbuffer = OpenRTM_aist.CdrBufferFactory.instance().createObject("ring_buffer")
    if self._eventbuffer is None:
        self._rtcout.RTC_ERROR("default buffer creation failed")
    self._eventbuffer.init(buff_prop)


    if not self._bufferzeromode:
      self._writable_listener = CSPEventPort.IsWritableListener(self._eventbuffer, self._ctrl, self._channeltimeout, self, self._fsm)
      self._write_listener = CSPEventPort.WriteListener(self._ctrl)
    else:
      self._writable_listener = CSPEventPort.IsWritableZeroModeListener(self._ctrl, self._channeltimeout, self, self._fsm)
      self._write_listener = CSPEventPort.WriteZeroModeListener(self._ctrl)

  ##  
  # @if jp
  #
  # @brief 書き込み処理を開始したコネクタを登録
  #
  # @param self
  # @param con InPortConnector
  # 
  #
  # @else
  #
  # @brief 
  #
  # @param self
  # @param con
  #
  # @endif
  #
  def setWritingConnector(self, con):
    self._writingConnector = con

  ##
  # @if jp
  #
  # @brief 接続先のOutPortに入力可能であることを通知
  # バッファがフルになる、もしくは待機中のOutPortがなくなるまで、接続先のコネクタのデータを読み込む
  # バッファからデータを読み込んだ場合は、この関数を呼び出す必要がある
  #
  # @param self
  # 
  #
  # @else
  #
  # @brief 
  #
  # @param self
  #
  # @endif
  #
  def notify(self):
    for con in self._connectors:
      guard_ctrl = OpenRTM_aist.ScopedLock(self._ctrl._cond)
      if self._ctrl._writing:
        self._ctrl._cond.wait(self._channeltimeout)
      if not self._eventbuffer.full():
        if con.isReadable():
          ret, _ = con.readBuff()
          if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
            pass
          else:
            self._rtcout.RTC_ERROR("read error:%s",(OpenRTM_aist.DataPortStatus.toString(ret)))
          
  ##
  # @if jp
  #
  # @brief コネクタ接続関数
  # InPortBaseの接続処理のほかに、コネクタに書き込み確認時、書き込み時のコールバック関数を設定する
  #
  # @param self
  # @param connector_profile コネクタプロファイル
  # @return ret, prof
  # ret：リターンコード
  # prof：コネクタプロファイル
  # 
  # @return ポート名称
  #
  # @else
  #
  # @brief Get port name
  #
  # @param self
  # @param connector_profile 
  # @return ret, prof
  #
  # @endif
  #
  def notify_connect(self, connector_profile):
    ret, prof = super(CSPEventPort, self).notify_connect(connector_profile)
    guard_con = OpenRTM_aist.ScopedLock(self._connector_mutex)
    for con in self._connectors:
      con.setIsWritableListener(self._writable_listener)
      con.setWriteListener(self._write_listener)
    return (ret, prof)

  ##
  # @if jp
  #
  # @brief リングバッファ使用モード時のデータ読み込み処理
  # バッファがemptyではない場合はバッファから読み込む
  # コネクタの中に読み込み可能なものがある場合は、そのコネクタから読み込む
  # ただし、書き込み中の場合は書き込み終了までブロックする
  #
  # @param self
  # @param connector_profile コネクタプロファイル
  # @return ret, prof
  # ret：True：読み込み成功、False：バッファがemptyでかつ読み込み可能なコネクタが存在しない
  # data：データ
  # 
  #
  # @else
  #
  # @brief 
  #
  # @param self
  # @return ret, data
  #
  # @endif
  #
  def dataPullBufferMode(self):
    guard_con = OpenRTM_aist.ScopedLock(self._connector_mutex)
    if not self._connectors:
      self._rtcout.RTC_DEBUG("no connectors")
      return False, None

    if self._eventbuffer.empty():
      for con in self._connectors:
        guard_ctrl = OpenRTM_aist.ScopedLock(self._ctrl._cond)
        if not self._eventbuffer.empty():
          value = [None]
          self._eventbuffer.read(value)
          del guard_ctrl
          self.notify()
          return True, value[0]
        elif self._ctrl._writing:
          self._ctrl._cond.wait(self._channeltimeout)
          value = [None]
          if not self._eventbuffer.empty():
            self._eventbuffer.read(value)
            del guard_ctrl
            self.notify()
            return True, value[0]
          else:
            self._rtcout.RTC_ERROR("read timeout")
            return False, None
        else:
          readable = con.isReadable()
          if readable:
            ret, _ = con.readBuff()
            value = [None]
            self._eventbuffer.read(value)
            if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
              return True, value[0]
            else:
              self._rtcout.RTC_ERROR("read error:%s",(OpenRTM_aist.DataPortStatus.toString(ret)))
              return False, None
    else:
      value = [None]
      guard_ctrl = OpenRTM_aist.ScopedLock(self._ctrl._cond)
      if not self._eventbuffer.empty():
        self._eventbuffer.read(value)
        del guard_ctrl
        self.notify()
        return True, value[0]
      else:
        self._rtcout.RTC_ERROR("read error:%s",(OpenRTM_aist.BufferStatus.toString(ret)))
        del guard_ctrl
        self.notify()
        return False, None
    return False, None

  ##
  # @if jp
  #
  # @brief 非リングバッファ使用モード時のデータ読み込み処理
  # データ読み込み可能なコネクタが存在する場合は、そのコネクタからデータを読み込む
  # 
  #
  # @param self
  # @param connector_profile コネクタプロファイル
  # @return ret, data
  # ret：True：読み込み成功、False：データ読み込み可能なコネクタが存在しない
  # data：データ(読み込み失敗の場合はNone)
  # 
  #
  # @else
  #
  # @brief 
  #
  # @param self
  # @return ret, data
  #
  # @endif
  #
  def dataPullZeroMode(self):
    guard_con = OpenRTM_aist.ScopedLock(self._connector_mutex)
    for con in self._connectors:
      if con.isReadable():
        guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
        ret, _ = con.readBuff()
        value = [None]
        self._eventbuffer.read(value)
        if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
          return True, value[0]
        else:
          self._rtcout.RTC_ERROR("read error:%s",(OpenRTM_aist.DataPortStatus.toString(ret)))
          return False, None
    return False, None

  ##
  # @if jp
  #
  # @brief データ読み込み可能なコネクタを選択し、
  # self._valueに読み込んだデータを格納する
  # 
  #
  # @param self
  # @return True：読み込み成功、False：読み込み不可
  #
  #
  # @else
  #
  # @brief 
  #
  # @param self
  # @return 
  #
  # @endif
  #
  def select(self):
    self._rtcout.RTC_TRACE("select()")
    if not self._bufferzeromode:
      ret, value = self.dataPullBufferMode()
    else:
      ret, value = self.dataPullZeroMode()
    guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
    if ret:
      self._value = value
    return ret
    
  ##
  # @if jp
  #
  # @brief select関数で格納したデータの取得
  # 
  #
  # @param self
  # @return データ
  #
  #
  # @else
  #
  # @brief 
  #
  # @param self
  # @return 
  #
  # @endif
  #
  def readData(self):
    guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
    self._rtcout.RTC_TRACE("readData()")
    if self._OnRead is not None:
      self._OnRead()
      self._rtcout.RTC_TRACE("OnRead called")

    if self._ctrl._writing:
      self._ctrl._cond.wait(self._channeltimeout)

    if self._writingConnector:
      self._writingConnector = None
      if not self._eventbuffer.empty():
        value = [None]
        self._eventbuffer.read(value)
        return value[0]

    return self._value

  ##
  # @if jp
  #
  # @brief データを読み込み可能なコネクタを選択しデータを取得する
  # 読み込み可能なコネクタが存在しない場合は待機する
  # 
  #
  # @param self
  # @return データ(タイムアウトした場合はNone)
  #
  #
  # @else
  #
  # @brief 
  #
  # @param self
  # @return 
  #
  # @endif
  #
  def read(self):
    self._rtcout.RTC_TRACE("DataType read()")
    if self._OnRead is not None:
      self._OnRead()
      self._rtcout.RTC_TRACE("OnRead called")

    if not self._connectors:
      self._rtcout.RTC_DEBUG("no connectors")
      return None

    if not self._bufferzeromode:
      return self.readBufferMode()
    else:
      return self.readZeroMode()


  ##
  # @if jp
  #
  # @brief リングバッファ使用モード時のデータ読み込み処理
  # 読み込み可能なコネクタが存在しない場合は待機する
  # 
  #
  # @param self
  # @return データ(タイムアウトした場合はNone)
  #
  #
  # @else
  #
  # @brief 
  #
  # @param self
  # @return 
  #
  # @endif
  #
  def readBufferMode(self):
    ret, data = self.dataPullBufferMode()
    if ret:
      return data
    else:
      value = [None]
      guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
      if self._ctrl._writing or self._eventbuffer.empty():
        self._ctrl._cond.wait(self._channeltimeout)
      if not self._eventbuffer.empty():
        self._eventbuffer.read(value)

        return value[0]
      else:
        self._rtcout.RTC_ERROR("read timeout")
        return None

  ##
  # @if jp
  #
  # @brief 非リングバッファ使用モード時のデータ読み込み処理
  # 読み込み可能なコネクタが存在しない場合は待機する
  # 
  #
  # @param self
  # @return データ(タイムアウトした場合はNone)
  #
  #
  # @else
  #
  # @brief 
  #
  # @param self
  # @return 
  #
  # @endif
  #
  def readZeroMode(self):
    ret, data = self.dataPullZeroMode()
    if ret:
      return data
    else:
      guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
      self._ctrl._waiting = True
      self._ctrl._cond.wait(self._channeltimeout)
      self._ctrl._waiting = False
      value = [None]
      if not self._eventbuffer.empty():
        self._eventbuffer.read(value)
        return value[0]
      else:
        self._rtcout.RTC_ERROR("read timeout")
        return None

  def setOnRead(self, on_read):
    self._OnRead = on_read
    

  ##
  # @if jp
  #
  # @class IsWritableListener
  #
  # @brief データ書き込み時の確認リスナ基底クラス(リングバッファ使用モード)
  # 
  #
  # @since 2.0.0
  #
  # @else
  #
  # @class IsWritableListener
  #
  # @brief 
  #
  #
  # @since 2.0.0
  #
  # @endif
  #
  class IsWritableListener(OpenRTM_aist.IsWritableListenerBase):
    ##
    # @if jp
    #
    # @brief コンストラクタ
    # 
    #
    # @param self
    # @param buff リングバッファ
    # @param control WorkerThreadCtrlオブジェクト
    # @param timeout 書き込み待機のタイムアウト
    # @param manager CSPチャネル管理マネージャ
    # managerを指定した場合は、managerが待機中の場合にロック解除の通知を行う
    # 
    #
    #
    # @else
    #
    # @brief 
    #
    # @param self
    # @param buff 
    # @param control 
    # @param timeout 
    # @param manager 
    #
    # @endif
    #
    def __init__(self, buff, control, timeout, port, manager=None):
      self._ctrl = control
      self._buffer = buff
      self._channeltimeout = timeout
      self._manager = manager
      self._port = port
    ##
    # @if jp
    #
    # @brief 書き込み確認時のコールバック関数
    # 他のコネクタがデータ書き込み中の場合は完了まで待機する
    # バッファがフルではない場合は書き込み状態に移行する
    # このため、書き込み可能な場合は必ずデータを書き込む必要がある
    # 
    #
    # @param self
    # @param con InPortConnector
    # @return True：書き込み可能、False：書き込み不可
    # 
    #
    #
    # @else
    #
    # @brief 
    #
    # @param self
    # @param con 
    # @return
    #
    # @endif
    #
    def __call__(self, con):
      if self._manager:
        if self._manager.notify(inport=self._port):
          return True
      guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
      if self._ctrl._writing:
        self._ctrl._cond.wait(self._channeltimeout)
      if not self._buffer.full():
        self._ctrl._writing = True
        return True
      else:
        self._ctrl._writing = False
        return False

  ##
  # @if jp
  #
  # @class WriteListener
  #
  # @brief データ書き込み時のリスナ基底クラス(リングバッファ使用モード)
  # 
  #
  # @since 2.0.0
  #
  # @else
  #
  # @class WriteListener
  #
  # @brief 
  #
  #
  # @since 2.0.0
  #
  # @endif
  #
  class WriteListener(OpenRTM_aist.WriteListenerBase):
    ##
    # @if jp
    #
    # @brief コンストラクタ
    # 
    #
    # @param self
    # @param control WorkerThreadCtrlオブジェクト
    # 
    #
    #
    # @else
    #
    # @brief 
    #
    # @param self
    # @param control 
    #
    # @endif
    #
    def __init__(self, control):
      self._ctrl = control
    ##
    # @if jp
    #
    # @brief 書き込み時のコールバック関数
    # CSPEventPortではバッファへの書き込みはON_RECEIVEDコールバックで実行するため、
    # 書き込み状態の解除のみを行う。
    # 
    #
    # @param self
    # @param data データ
    # @return リターンコード
    # BUFFER_OK：正常完了
    # 
    #
    #
    # @else
    #
    # @brief 
    #
    # @param self
    # @param data 
    # @return
    #
    # @endif
    #
    def __call__(self, data):
      guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
      self._ctrl._writing = False
      self._ctrl._cond.notify()
      return OpenRTM_aist.BufferStatus.BUFFER_OK

  ##
  # @if jp
  #
  # @class IsWritableZeroModeListener
  #
  # @brief データ書き込み確認リスナ基底クラス(非リングバッファ使用モード)
  # 
  #
  # @since 2.0.0
  #
  # @else
  #
  # @class IsWritableZeroModeListener
  #
  # @brief 
  #
  #
  # @since 2.0.0
  #
  # @endif
  #
  class IsWritableZeroModeListener(OpenRTM_aist.IsWritableListenerBase):
    ##
    # @if jp
    #
    # @brief コンストラクタ
    # 
    #
    # @param self
    # @param buff リングバッファ
    # @param control WorkerThreadCtrlオブジェクト
    # @param timeout 書き込み待機のタイムアウト
    # @param manager CSPチャネル管理マネージャ
    # managerを指定した場合は、managerが待機中の場合にロック解除の通知を行う
    # 
    #
    #
    # @else
    #
    # @brief 
    #
    # @param self
    # @param buff 
    # @param control 
    # @param timeout 
    # @param manager 
    #
    # @endif
    #
    def __init__(self, control, timeout, port, manager=None):
      self._ctrl = control
      self._channeltimeout = timeout
      self._manager = manager
      self._port = port
    ##
    # @if jp
    #
    # @brief 書き込み確認時のコールバック関数
    # 他のコネクタがデータ書き込み中の場合は完了まで待機する
    # バッファがフルではない場合は書き込み状態に移行する
    # このため、書き込み可能な場合は必ずデータを書き込む必要がある
    # 
    #
    # @param self
    # @param con InPortConnector
    # @return True：書き込み可能、False：書き込み不可
    # 
    #
    #
    # @else
    #
    # @brief 
    #
    # @param self
    # @param con 
    # @return
    #
    # @endif
    #
    def __call__(self, con):
      if self._manager:
        if self._manager.notify(inport=self._port):
          return True
      guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
      if self._ctrl._waiting and self._ctrl._writing:
        self._ctrl._cond.wait(self._channeltimeout)
      if self._ctrl._waiting:
        self._ctrl._writing = True
        return True
      else:
        self._ctrl._writing = False
        return False
        
  ##
  # @if jp
  #
  # @class WriteZeroModeListener
  #
  # @brief データ書き込み時のリスナ基底クラス(非リングバッファ使用モード)
  # 
  #
  # @since 2.0.0
  #
  # @else
  #
  # @class WriteZeroModeListener
  #
  # @brief 
  #
  #
  # @since 2.0.0
  #
  # @endif
  #
  class WriteZeroModeListener(OpenRTM_aist.WriteListenerBase):
    ##
    # @if jp
    #
    # @brief コンストラクタ
    # 
    #
    # @param self
    # @param control WorkerThreadCtrlオブジェクト
    # 
    #
    #
    # @else
    #
    # @brief 
    #
    # @param self
    # @param control 
    #
    # @endif
    #
    def __init__(self, control):
      self._ctrl = control
    ##
    # @if jp
    #
    # @brief 書き込み時のコールバック関数
    # CSPEventPortではバッファへの書き込みはON_RECEIVEDコールバックで実行するため、
    # 書き込み状態の解除のみを行う。
    # 
    #
    # @param self
    # @param data データ
    # @return リターンコード
    # BUFFER_OK：正常完了
    # 
    #
    #
    # @else
    #
    # @brief 
    #
    # @param self
    # @param data
    # @return
    #
    # @endif
    #
    def __call__(self, data):
      guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
      self._ctrl._writing = False
      self._ctrl._cond.notify()
      return OpenRTM_aist.BufferStatus.BUFFER_OK
        

  class WorkerThreadCtrl:
    def __init__(self):
      self._mutex = threading.RLock()
      self._cond = threading.Condition(self._mutex)
      self._writing = False
      self._waiting = False

