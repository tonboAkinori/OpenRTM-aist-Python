#!/usr/bin/env python
# -*- coding: euc-jp -*-


##
# @file OutPortPullConnector.py
# @brief OutPortPull type connector class
# @date $Date$
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2009
#     Noriaki Ando
#     Task-intelligence Research Group,
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#

import OpenRTM_aist


class OutPortPullConnector(OpenRTM_aist.OutPortConnector):

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # OutPortPullConnector は OutPortProvider の所有権を持つ。
    # したがって、OutPortPullConnector 削除時には、OutPortProvider も同時に
    # 解体・削除される。
    #
    # @param profile pointer to a ConnectorProfile
    # @param provider pointer to an OutPortProvider
    # @param buffer pointer to a buffer
    #
    # @elsek
    # @brief Constructor
    #
    # OutPortPullConnector assume ownership of InPortConsumer.
    # Therefore, OutPortProvider will be deleted when OutPortPushConnector
    # is destructed.
    #
    # @param profile pointer to a ConnectorProfile
    # @param provider pointer to an OutPortProvider
    # @param buffer pointer to a buffer
    #
    # @endif
    #
    # OutPortPullConnector(ConnectorInfo info,
    #                      OutPortProvider* provider,
    #                      CdrBufferBase* buffer = 0);
    def __init__(self, info, provider, buffer = 0):
        OpenRTM_aist.OutPortConnector.__init__(self, info)
        self._provider = provider
        self._buffer = buffer
        self.onConnect()
        return


    ##
    # @if jp
    # @brief デストラクタ
    #
    # disconnect() が呼ばれ、provider, buffer が解体・削除される。
    #
    # @else
    #
    # @brief Destructor
    #
    # This operation calls disconnect(), which destructs and deletes
    # the consumer, the publisher and the buffer.
    #
    # @endif
    #
    def __del__(self):
        self.onDisConnect()
        self.disconnect()
        return

    ##
    # @if jp
    # @brief データの書き込み
    #
    # Publisherに対してデータを書き込み、これにより対応するInPortへ
    # データが転送される。
    #
    # @else
    #
    # @brief Writing data
    #
    # This operation writes data into publisher and then the data
    # will be transferred to correspondent InPort.
    #
    # @endif
    #
    # virtual ReturnCode write(const cdrMemoryStream& data);
    def write(self, data):
        self._buffer.write(data)
        return self.PORT_OK


    ##
    # @if jp
    # @brief 接続解除
    #
    # consumer, publisher, buffer が解体・削除される。
    #
    # @else
    #
    # @brief disconnect
    #
    # This operation destruct and delete the consumer, the publisher
    # and the buffer.
    #
    # @endif
    #
    # virtual ReturnCode disconnect();
    def disconnect(self):
        return self.PORT_OK


    ##
    # @if jp
    # @brief Buffer を取得する
    #
    # Connector が保持している Buffer を返す
    #
    # @else
    # @brief Getting Buffer
    #
    # This operation returns this connector's buffer
    #
    # @endif
    #
    # virtual CdrBufferBase* getBuffer();
    def getBuffer(self):
        return self._buffer


    ##
    # @if jp
    # @brief アクティブ化
    #
    # このコネクタをアクティブ化する
    #
    # @else
    #
    # @brief Connector activation
    #
    # This operation activates this connector
    #
    # @endif
    #
    # virtual void activate(){}; // do nothing
    def activate(self):  # do nothing
        pass

    ##
    # @if jp
    # @brief 非アクティブ化
    #
    # このコネクタを非アクティブ化する
    #
    # @else
    #
    # @brief Connector deactivation
    #
    # This operation deactivates this connector
    #
    # @endif
    #
    # virtual void deactivate(){}; // do nothing
    def deactivate(self): # do nothing
        pass

    
    ##
    # @if jp
    # @brief 接続確立時にコールバックを呼ぶ
    # @else
    # @brief Invoke callback when connection is established
    # @endif
    # void onConnect()
    def onConnect(self):
        self._listeners.connector_[OpenRTM_aist.ConnectorListenerType.ON_CONNECT].notify(self._profile)
        return

    ##
    # @if jp
    # @brief 接続切断時にコールバックを呼ぶ
    # @else
    # @brief Invoke callback when connection is destroied
    # @endif
    # void onDisconnect()
    def onDisconnect(self):
        self._listeners.connector_[OpenRTM_aist.ConnectorListenerType.ON_DISCONNECT].notify(self._profile)
        return
