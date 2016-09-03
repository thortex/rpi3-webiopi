#   Copyright 2014 Andreas Riegg - t-h-i-n-x.net
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#   Changelog
#
#   1.0    2014-08-25    Initial release.
#   1.1    2014-09-04    Improved file open/close handling.
#                        Reimplemented writeMemoryBytes().
#
#   Config parameters
#
#   - slots         integer       Number of memory bytes
#   - filename      string        Name/path of pickle memory file
#
#   Usage remarks
#
#   - This class is mainly targeted to store some 100's of bytes on the
#     server disk.
#     It is abolutely NOT suited to save 10's of kilobytes or even more.
#     Values are kept in server RAM, so reading is very fast but allocates
#     server RAM memory, so be sparse on slot sizes. Every update
#     is written immediately to disk, so writing is slower and initiates
#     server disk activity for every write.
#   - Multiple device instances are possible within one server. Make sure
#     to have different filenames/pathes for each device instance via the
#     filename parameter
#   - Slot sizes can be changed at every instance creation time. If old size
#     was smaller, the slots will be filled from the first slot until done.
#     Remaining slots will be initialized with 0x00. If old size was bigger,
#     the slots will be filled to the last available slot and the remainder
#     of the old slot bytes will be discarded.
#

import os
import pickle
from webiopi.utils.types import toint
from webiopi.devices.memory import Memory

class PICKLEFILE(Memory):
#   This class uses the standard Pickle utility of Python to store the
#   bytes.

#---------- Constants and definitions ----------
    BYTES = []
    
    FILENAME_DEFAULT = "webiopimem.pkl" # Local memory default name
    MAXSLOT_VALUE    = 1024

#---------- Class initialisation ----------

    def __init__(self, slots=256, filename=None):
        slots = toint(slots)
        if not slots in range(1, self.MAXSLOT_VALUE + 1):
            raise ValueError("slots value [%d] out of range [%d..%d]" % (slots, 1, self.MAXSLOT_VALUE))

        self._outputfile = None
        
        if filename != None:
            self.filename = filename
        else:
            self.filename = self.FILENAME_DEFAULT
        
        Memory.__init__(self, slots)
        self.BYTES = [0 for i in range (0, slots )]

        if os.path.exists(self.filename):
            self.__readFile__()


#---------- Abstraction framework contracts ----------
            
    def __str__(self):
        return "PICKLEFILE (%s)" % self.filename

    def close(self):
        if self._outputfile is not None:
            self._outputfile.close()
    
#---------- Memory abstraction related methods ----------

    def __readMemoryByte__(self, address):
        return self.BYTES[address]

    def __writeMemoryByte__(self, address, value):
        self.BYTES[address] = value
        self.__writeFile__()
        return self.__readMemoryByte__(address)
    

#---------- Memory abstraction NON-REST re-implementation ----------
# Avoid file writing for every byte, do this for all bytes at the end

    def writeMemoryBytes(self, byteValues, start=0):
        count = self.byteCount()
        i = 0
        for byte in byteValues: # do nothing if list is empty
            position = i + start
            if position >= count:
                break # truncate silent
            if position < 0:
                pass # adjust silent
            else:
                self.BYTES[i + start] = byte
            i += 1
        self.__writeFile__()


#---------- Local helpers ----------

    def __readFile__(self):
        with open(self.filename, "rb") as f:
            filebytes = pickle.load(f)
            
        byteCountFile = len(filebytes)
        if (byteCountFile > self.byteCount()):
            slots = self.byteCount()
        else:
            slots = byteCountFile
        for i in range (0, slots ):
            self.BYTES[i] = filebytes[i]

    def __writeFile__(self):
        if self._outputfile is None:
            self._outputfile = open(self.filename, "wb")
        pickle.dump(self.BYTES, self._outputfile)
                             
