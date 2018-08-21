#pragma rtGlobals=3		// Use modern global access method and strict wave access.

// to have a separate entry in main menu
//Menu "Abf"
//	"Import ABf file",HT_ImportAbfFile()
//End

// to extend "Data" menu
Menu "Data"
	"--"
	"Import ABf file",HT_ImportAbfFile()
End

Proc HT_ImportAbfFile(filePathName,basename,channelNumberFlag,channelNumberTypeFlag,nameCleanupFlag,channelIDInNameFlag,gapFreeFlag)
	String filePathName,basename
	Variable channelNumberFlag
	Variable channelNumberTypeFlag=2 // default is physical channel
	Variable nameCleanupFlag=1 // default is to clean up names if necessary
	Variable channelIDInNameFlag=2 // default is to use physical channel IDs in the wave names
	Variable gapFreeFlag=1
	Prompt filePathName, "Filename (empty for dialog):"
	Prompt basename, "Base name of waves (empty for filename):"
	Prompt channelNumberFlag, "Channel # to read:", popup, "all acquired;0;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15"
	Prompt channelNumberTypeFlag, "Channel # identifies...", popup, "logical channel number;physical channel number"
	Prompt nameCleanupFlag, "Cleanup wave name?", popup, "no -> allow liberal names;yes -> disallow liberal names;"
	Prompt channelIDInNameFlag, "Channel # used to build wave name:", popup, "logical channel number;physical channel number;"
	Prompt gapFreeFlag, "Read gap-free data into...", popup, "a single wave;one wave for each episode"
	PauseUpdate; Silent 1
	// channelFlag is in range 1...17
	// channel parameter should be 0... last possible channel, or -1 meaning all available channels
	fHT_ImportAbfFile(filePathName,basename,channelNumberFlag-2,channelNumberTypeFlag,nameCleanupFlag,channelIDInNameFlag,gapFreeFlag) 
End

// (1) Gap Free. (nOperationMode = 3)
// (2) Variable-Length Event-Driven. (nOperationMode = 1)
// (3) Fixed-Length Event-Driven. (nOperationMode = 2)
// (4) High-Speed Oscilloscope Mode. (nOperationMode = 4)
// (5) Episodic Stimulation Mode. (nOperationMode = 5)

// the following string lists are used to convert to base units, correct order is absolutely essential
Strconstant ABF_UNIT_STRINGS="pA;nA;µA;mA;pV;nV;µV;mV"
Strconstant ABF_BASEUNIT_STRINGS="A;A;A;A;V;V;V;V"
Strconstant ABF_UNIT_SCALINGS="1e-12;1e-9;1e-6;1e-3;1e-12;1e-9;1e-6;1e-3"

// channel: logical channel to read, -1 for all acquired channels
Function fHT_ImportAbfFile(filePathName,basename,channel,channelNumberTypeFlag,nameCleanupFlag,channelIDInNameFlag,gapFreeFlag)
	String filePathName,basename
	Variable channel,channelNumberTypeFlag,nameCleanupFlag,channelIDInNameFlag,gapFreeFlag

	Variable channelCount,episodeCount,sampleCount,operationMode,i,j,asciCode,logicalChannel,physicalChannel,totalSampleCount,unitIdx // ,startTime
	String thisWaveName,fileName,fileTitle,ADCSamplingSeq//,metaData

	if (strlen(filePathName)==0)
		filePathName=bpc_AbfFileOpenDialog("Select ABF file to open","",1)
	endif
	if (strlen(filePathName)==0)
		printf "ERROR: expecting file name\r"
		return 0
	endif
	fileName=bpc_AbfFileStripPathName(filePathName)
	fileTitle=bpc_AbfFileStripExt(fileName)
	
	if ((bpc_AbfIsAbfFile(filePathName)==0) || (bpc_AbfHasData(filePathName)==0))
		printf "ERROR %d: %s\r",bpc_AbfLastErr(),bpc_AbfLastErrStr() 
		return 0
	endif
		
//		dump out all meta-data
//		bpc_AbfPrintMetaData(filePathName)
//		or store into a string
//		if (!bpc_AbfMetaData(filePathName,metaData))
//			printf "ERROR %d: %s\r",bpc_AbfLastErr(),bpc_AbfLastErrStr() 
//			return 0
//		endif		
		
	if (!bpc_AbfOperationMode(filePathName,operationMode))
		printf "ERROR %d: %s\r",bpc_AbfLastErr(),bpc_AbfLastErrStr() 
		return 0
	endif
				
	if (!bpc_AbfChannelCount(filePathName,channelCount))
		printf "ERROR %d: %s\r",bpc_AbfLastErr(),bpc_AbfLastErrStr() 
		return 0
	endif

	if (!bpc_AbfEpisodeCount(filePathName,episodeCount))
		printf "ERROR %d: %s\r",bpc_AbfLastErr(),bpc_AbfLastErrStr() 
		return 0
	endif				

	if (!bpc_AbfADCSamplingSeq(filePathName,ADCSamplingSeq))
		printf "ERROR %d: %s\r",bpc_AbfLastErr(),bpc_AbfLastErrStr() 
		return 0
	endif
	
	if (ItemsInList(ADCSamplingSeq)!=channelCount) // sanity check, should never happen
		printf "UNEXPECTED ERROR: channelCount (%d) <> # of items in ADCSamplingSeq (%d)\r",ItemsInList(ADCSamplingSeq),channelCount
		return 0
	endif
	
	if (strlen(basename)==0)
		basename=fileTitle
	endif

	if (nameCleanupFlag==2)
		asciCode=char2num(basename)
		if (!((asciCode>=65 && asciCode<=90) || (asciCode>=97 && asciCode<=122)))
			basename="A"+basename // have 'A' in front of wavename, may be nicer than default 'X'
		endif
		basename=CleanupName(basename,0)
	endif
	
	if (channel<0) // user wants to import all acquired channels
	
		if (operationMode==3 && gapFreeFlag==1) // this is gap-free data, the user wants to read it into a single wave
		
			if (!bpc_AbfTotalSampleCount(filePathName,totalSampleCount)) // samples in this episode
				printf "ERROR %d: %s\r",bpc_AbfLastErr(),bpc_AbfLastErrStr() 
				return 0
			endif		
			for (j=0;j<channelCount;j+=1) // loop through all acquired channels												
				if (channelIDInNameFlag==1)
					sprintf thisWaveName,"%s_ch%d",basename,j
				else
					sprintf thisWaveName,"%s_ch%s",basename,StringFromList(j,ADCSamplingSeq,";")
				endif
				Make/O/N=(totalSampleCount) $thisWaveName=NaN
				Wave thisWave=$thisWaveName
				if (!bpc_AbfChannelRead(filePathName,j,thisWave))
					printf "ERROR %d: %s\r",bpc_AbfLastErr(),bpc_AbfLastErrStr() 
					return 0
				endif					
			endfor	
			
		else // this either nor gap-free data or user wants to load episodes anyway (the latter is unlikely)
			for (i=1;i<=episodeCount;i+=1) // loop through all episodes stored in file
				for (j=0;j<channelCount;j+=1) // loop through all acquired channels
					if (channelIDInNameFlag==1)
						sprintf thisWaveName,"%s_ch%dep%d",basename,j,i
					else
						sprintf thisWaveName,"%s_ch%sep%d",basename,StringFromList(j,ADCSamplingSeq,";"),i
					endif
					
//					if (!bpc_AbfStartTime(filePathName,j,i,startTime))
//						printf "ERROR %d: %s\r",bpc_AbfLastErr(),bpc_AbfLastErrStr() 
//						return 0
//					endif
		
					if (!bpc_AbfSampleCount(filePathName,i,sampleCount)) // samples in this episode
						printf "ERROR %d: %s\r",bpc_AbfLastErr(),bpc_AbfLastErrStr() 
						return 0
					endif		
												
					Make/O/N=(sampleCount) $thisWaveName=NaN
					Wave thisWave=$thisWaveName
					if (!bpc_AbfEpisodeRead(filePathName,j,i,thisWave))
						printf "ERROR %d: %s\r",bpc_AbfLastErr(),bpc_AbfLastErrStr() 
						return 0
					endif

					unitIdx=WhichListItem(WaveUnits(thisWave,1),ABF_UNIT_STRINGS,";")
					if (unitIdx>=0)
						SetScale d 0,0,StringFromList(unitIdx,ABF_BASEUNIT_STRINGS,";"), thisWave
						FastOp thisWave=(str2num(StringFromList(unitIdx,ABF_UNIT_SCALINGS,";")))*thisWave
					endif

					Make/O/N=(sampleCount) $(thisWaveName + "_wf")/Wave=stimset
					stimset = NaN
					if (!bpc_AbfEpisodeWaveform(filePathName,j,i,stimset))
						printf "ERROR %d: %s\r",bpc_AbfLastErr(),bpc_AbfLastErrStr() 
						return 0
					endif

				endfor
			endfor
		endif
		
	else  // if (channel<0), user wants to import a specific channel, may be logical or physical
	
		if (channelNumberTypeFlag==1) // channel # is logical -> map logical to physical channel
			logicalChannel=channel
			if (logicalChannel>=channelCount)  // sanity check, logical channels start with 0
				printf "ERROR: logical channel #%d is invalid (not acquired in file '%s').\r",logicalChannel,fileName
				return 0
			endif			
			physicalChannel=str2num(StringFromList(channel,ADCSamplingSeq,";"))										
		else // channel # is physical -> map physical to logical channel
			physicalChannel=channel
			logicalChannel=WhichListItem(num2str(physicalChannel),ADCSamplingSeq,";")				
			if (logicalChannel<0) // sanity check
				printf "ERROR: physical channel #%d is invalid (not acquired in file '%s').\r",physicalChannel,fileName
				return 0
			endif
		endif			
				
		if (operationMode==3 && gapFreeFlag==1) // this is gap-free data, the user wants to read it into a single wave

			if (!bpc_AbfTotalSampleCount(filePathName,totalSampleCount)) // samples in this episode
				printf "ERROR %d: %s\r",bpc_AbfLastErr(),bpc_AbfLastErrStr() 
				return 0
			endif
			sprintf thisWaveName,"%s_ch%d",basename,(channelIDInNameFlag==1) ? logicalChannel : physicalChannel
			Make/O/N=(totalSampleCount) $thisWaveName=NaN
			Wave thisWave=$thisWaveName
			if (!bpc_AbfChannelRead(filePathName,logicalChannel,thisWave))
				printf "ERROR %d: %s\r",bpc_AbfLastErr(),bpc_AbfLastErrStr() 
				return 0
			endif
		
		else // this either nor gap-free data or user wants to load episodes anyway (the latter is unlikely)
		
			for (i=1;i<=episodeCount;i+=1) // loop through all episodes stored in file
	
				sprintf thisWaveName,"%s_ch%d",basename,(channelIDInNameFlag==1) ? logicalChannel : physicalChannel
	
				if (!bpc_AbfSampleCount(filePathName,i,sampleCount)) // samples in this episode
					printf "ERROR %d: %s\r",bpc_AbfLastErr(),bpc_AbfLastErrStr() 
					return 0
				endif				
				Make/O/N=(sampleCount) $thisWaveName=NaN
				Wave thisWave=$thisWaveName
				if (!bpc_AbfEpisodeRead(filePathName,logicalChannel,i,thisWave))
					printf "ERROR %d: %s\r",bpc_AbfLastErr(),bpc_AbfLastErrStr() 
					return 0
				endif
				
				unitIdx=WhichListItem(WaveUnits(thisWave,1),ABF_UNIT_STRINGS,";")
				if (unitIdx>=0)
					SetScale d 0,0,StringFromList(unitIdx,ABF_BASEUNIT_STRINGS,";"), thisWave
					FastOp thisWave=(str2num(StringFromList(unitIdx,ABF_UNIT_SCALINGS,";")))*thisWave
				endif
				
			endfor
		endif
	endif // if (channel<0)
	
	return 1 // success

End

// allow dropping *.abf files onto running Igor instance
Static Function BeforeFileOpenHook(refNum,fileName,pathName,type,creator,kind)
	Variable refNum,kind
	String fileName,pathName,type,creator

	String sWinStylePath
	PathInfo $pathName
	//printf "fileName = %s, pathName = %s, type = %s, creator = %s, S_path = %s, kind = %d", fileName,pathName,type,creator,S_path,kind
	if ((kind==0) && (cmpstr(type,".abf")==0))
		DoAlert/T="Import ABF file" 1, "Would you like to import ABF file '"+fileName+"' into the current experiment?"
		if (V_Flag==1)
			sWinStylePath=ParseFilePath(5, S_path+fileName, "\\", 0, 0)
			//print "HT_ImportAbfFile(\""+ReplaceString("\\",sWinStylePath,"\\\\")+"\",)"
			Execute "HT_ImportAbfFile(\""+ReplaceString("\\",sWinStylePath,"\\\\")+"\",)" // escape '\'
			return 1 // do no processing
		endif
	endif
	return 0 // do normal processing
End
