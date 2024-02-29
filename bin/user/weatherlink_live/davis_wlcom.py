# Copyright © 2022 Javier Achirica
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
import select
import threading
import time
import socket
import struct
import os

from user.weatherlink_live.static.packets import packets, DataStructureType, KEY_TS, KEY_CONDITIONS, KEY_DATA_STRUCTURE_TYPE, KEY_TRANSMITTER_ID, WLC_START, WLC_END, WLC_SET_HISTRATE, WLC_LOOP_STA, WLC_LOOP_INT, WLC_LOOP_BAR, WLC_HIST_WLL, WLC_HIST_STA, WLC_HIST_INT, WLC_HIST_BAR
from user.weatherlink_live.packets import WlWlcomPacket
from user.weatherlink_live.service import WllService
from weewx import WeeWxIOError

GUARD_TIME = 300
MSG_TIMEOUT = 28
# Locking mechanism for safe shutdown
LOCK_FILE = '/tmp/weewx-wlcom.lck'
SHUTDOWN_FILE = '/tmp/weewx-wlcom.shut'

log = logging.getLogger(__name__)


class WllWlcomReceiver(object):
    """Receive Wl.com transmission from WeatherLink Live"""

    def __init__(self, archive_interval: int, service: WllService, port: int, host):
        self.archive_interval = archive_interval
        self.port = port
        self.host = host

        self.wait_timeout = 5

        self.sock = []

        self.stop_signal = threading.Event()
        self.threads = []
        thread = threading.Thread(name='WLL-WlcomAccept', target=self._accept)
        thread.daemon = True
        thread.start()
        self.threads.append(thread)

        try:
            os.remove(LOCK_FILE)
        except OSError:
            pass

        self.acks = dict()
        self.pending_storage = False
        service.register_ack_callback(self.new_archive_record)

    def _accept(self):
        log.debug("Starting Wl.com accept")
        try:
            self.sock.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
            self.sock[0].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock[0].bind(('', self.port))
            self.sock[0].listen(1)

            client = None
            while not self.stop_signal.is_set():
                r, _, _ = select.select([self.sock[0]], [], [], self.wait_timeout)
                if not r:
                    continue

                client, host = self.sock[0].accept()
                self.sock.append(client)
                thread = threading.Thread(name='WLL-WlcomReception', target=self._reception, args=(client,host))
                thread.daemon = True
                thread.start()
                self.threads.append(thread)

        except Exception as e:
            self.host.on_packet_receive_error(e)
            self.sock[0].shutdown(socket.SHUT_RDWR)
            self.sock[0].close()
            self.sock.pop(0)
            raise e

        self.sock[0].shutdown(socket.SHUT_RDWR)
        self.sock[0].close()
        self.sock.pop(0)

    def ack_packet(self, ts, is_timer):
        if ts not in self.acks:
            return

        sock, data, timer = self.acks[ts]
        del self.acks[ts]

        if timer:
            timer.cancel()

        if is_timer:
            try:
                open(LOCK_FILE, 'w').close()
            except FileExistsError:
                log.warn('Lock error. Closing')
                self.close()

        if os.path.isfile(SHUTDOWN_FILE) or self.stop_signal.is_set(): # Last chance to cancel
            return

        sock.send(struct.pack('<HBBHB13sH', WLC_START, 1, 15, 14, 0, data, WLC_END))

    def new_archive_record(self, event):
        if event.origin != 'software':
            self.ack_packet(event.record['dateTime'], False)
            try:
                os.remove(LOCK_FILE)
            except OSError:
                pass

    def _unpack(self, subpkt, pkttype, txid = None):
        keys, string, length = packets[pkttype]

        conditions = dict([ (k,v/d if v != n else None) for (k,d,t,n),v in zip(keys,struct.unpack(string, subpkt[:length]))])
        conditions[KEY_DATA_STRUCTURE_TYPE] = pkttype # % 100 - if we add loop packets too
        if txid:
            conditions[KEY_TRANSMITTER_ID] = txid
            
        return conditions

    def _reception(self, sock, host):
        log.debug("Starting Wl.com reception")
        start_time = time.time()
        did = None

        try:
            while not self.stop_signal.is_set():
                r, _, _ = select.select([sock], [], [], self.wait_timeout)
                if not r:
                    continue

                data = sock.recv(2048)
                log.debug(f"Received {len(data)} bytes")

                start, version, frametype, length, pkttime = struct.unpack('<HBBHI', data[:10])
                if start != WLC_START:
                    continue

                if frametype == 141:   # LOOP
                    settime = round(time.time()) != pkttime and time.time() < start_time + GUARD_TIME

                    #pktdict = { KEY_TS: pkttime, KEY_CONDITIONS: [] }

                    #subpkt = data[10:]
                    #txid = 1
                    #while len(subpkt) > 8:
                    #    #  txid cached from http packets
                    #    length, lsid, subtype, _, _ = struct.unpack('<HIBBB', subpkt[:9])
                    #    if lsid in self.host.txid:
                    #        txid = self.host.txid[lsid]
                    #
                    #    if subtype == 0:
                    #        conditions = self._unpack(subpkt[9:], WLC_LOOP_STA, txid)
                    #        txid += 1
                    #        pktdict[KEY_CONDITIONS].append(conditions)
                    #    elif subtype == 32:
                    #        pktdict[KEY_CONDITIONS].append(self._unpack(subpkt[9:], WLC_LOOP_BAR))
                    #    elif subtype == 33:
                    #        pktdict[KEY_CONDITIONS].append(self._unpack(subpkt[9:], WLC_LOOP_INT))
                    #    else:
                    #        log.info(f"Unknown loop subframe type {subtype} length {length}")

                    #    subpkt = subpkt[length + 2:]

                    sock.send(struct.pack('<HBBHB13sH', WLC_START, version, 15, 14, 0, data[3:16], WLC_END))

                    if settime:
                        is_dst = time.daylight and time.localtime().tm_isdst > 0
                        tzoffset = -int((time.altzone if is_dst else time.timezone) / 60)

                        sock.send(struct.pack('<HBBHBIIh5sH', WLC_START, version, 4, 16, 32, round(time.time()), did, tzoffset, b'', WLC_END))

                    #return WlWlcomPacket(pktdict, host)
                elif frametype == 144: # HISTORY
                    pktdict = { KEY_TS: pkttime, KEY_CONDITIONS: [] }

                    setrate = False
                    subpkt = data[10:]
                    txid = 1
                    while len(subpkt) > 8:
                        # txid cached from http packets
                        length, lsid, subtype, _, _ = struct.unpack('<HIBBB', subpkt[:9])
                        if lsid in self.host.txid:
                            txid = self.host.txid[lsid]

                        if subtype == 0:
                            conditions = self._unpack(subpkt[9:], WLC_HIST_STA, txid)
                            txid += 1
                            pktdict[KEY_CONDITIONS].append(conditions)
                            setrate = conditions['interval'] != self.archive_interval
                        elif subtype == 5:
                            pktdict[KEY_CONDITIONS].append(self._unpack(subpkt[9:], WLC_HIST_WLL))
                        elif subtype == 32:
                            pktdict[KEY_CONDITIONS].append(self._unpack(subpkt[9:], WLC_HIST_BAR))
                        elif subtype == 33:
                            pktdict[KEY_CONDITIONS].append(self._unpack(subpkt[9:], WLC_HIST_INT))
                        else:
                            log.info(f"Unknown history subframe type {subtype} length {length}")

                        subpkt = subpkt[length + 2:]

                    packet = WlWlcomPacket.try_create(pktdict, host)

                    if pkttime not in self.acks:
                        self.acks[pkttime] = [ sock, data[3:16], None ]

                    if pkttime < time.time() - self.archive_interval * 120:
                        # Ack backlog inmediately. If WeeWX crashes here, we're doomed...
                        self.ack_packet(pkttime, False)
                    else:
                        # Schedule timer in case callback is too late. let's delay as much as we can and hope for the best
                        ack = threading.Timer(MSG_TIMEOUT, self.ack_packet, args=(pkttime, True))
                        self.acks[pkttime][2] = ack
                        ack.daemon = True
                        ack.start()
                
                    self.host.on_packet_received(packet)

                    if setrate:
                        # Set history update rate to configured value
                        sock.send(struct.pack('<HBBHBIIIH10sHH', WLC_START, version, 4, 27, 33,
                                            round(time.time()), did, 12345, 12, WLC_SET_HISTRATE, self.archive_interval, WLC_END))

                elif frametype == 2: # AUTH REQ
                    subtype = data[6]

                    if subtype == 112:
                        did, challenge = struct.unpack('<IQ', data[11:23])
                        
                        # XXX TODO Generate response to challenge locally
                        wlcom = socket.create_connection(('wdi.weatherlink.com', 5621), 10)
                        wlcom.send(data)

                        auth = wlcom.recv(64)
                        wlcom.shutdown(socket.SHUT_RDWR)
                        wlcom.close()

                        start, _, _, _, _, _, response, _, _ = struct.unpack('<HBBHBIQQH', auth)
                        if start != WLC_START:
                            raise WeeWxIOError("Could not connect to wl.com for initial auth")

                        sock.send(struct.pack('<HBBHBIQQH', WLC_START, version, 3, 21, 112, round(time.time()), response, 0, WLC_END))
                    elif subtype == 113: # AUTH Response
                        # Confirm authentication
                        sock.send(struct.pack('<HBBHBIBH', WLC_START, version, 3, 6, 113, round(time.time()), 0, WLC_END))
                    else:
                        log.info(f"Unknown auth subframe type {subtype}")
                elif frametype == 8: # CFG OK
                    continue    # Ignore
                else:
                    log.info(f"Unknown packet type {frametype} length {length}")

        except Exception as e:
            self.host.on_packet_receive_error(e)
            self.sock.remove(sock)
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            raise e

        self.sock.remove(sock)
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()

    def close(self):
        log.debug("Stopping Wl.com reception")
        self.stop_signal.set()
        for thread in self.threads:
            thread.join(self.wait_timeout * 3)

        if self.threads[0].is_alive():
            log.warn("Wlcom accept thread still alive. Force closing socket")

        for sock in self.sock:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            self.sock.remove(sock)
            log.debug("Closed Wlcom sockets")

        try:
            os.remove(LOCK_FILE)
        except OSError:
            pass
        else:
            log.warn("Dropping unsaved record")

        log.debug("Stopped Wlcom reception")
