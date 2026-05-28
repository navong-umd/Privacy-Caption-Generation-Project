/*Application Package Name: com.tiktok.lite.go
class PRCS_421 {
/**
com.ss.mediakit.net.AVMDLMultiNetwork;alwayUpCellular(Landroid/content/Context;)Z
*/

    public static boolean alwayUpCellular(android.content.Context p3)
    {
        com.ss.mediakit.net.AVMDLMultiNetwork.initHandler(p3);
        if (com.ss.mediakit.net.AVMDLMultiNetwork.mCm != null) {
            try {
                com.ss.mediakit.net.AVMDLMultiNetwork.mCm.requestNetwork(new android.net.NetworkRequest$Builder().addCapability(12).addTransportType(0).build(), new com.ss.mediakit.net.AVMDLMultiNetwork$3());
                return 1;
            } catch (Exception v0_5) {
                v0_5.printStackTrace();
                return 0;
            }
        } else {
            return 0;
        }
    }

/**
com.ss.mediakit.medialoader.AVMDLDataLoader;startInternal()V
*/

    public final void startInternal()
    {
        this.mWriteLock.lock();
        try {
            if (this.mState != 1) {
                this.initLogThread(this);
                if (this.mHandle != 0) {
                    this.tryLoadP2pPluginInternal();
                    this.setConfigureInternal(this.mConfigure);
                    if (com.ss.mediakit.medialoader.AVMDLDataLoader._start(this.mHandle) >= 0) {
                        this.mState = 1;
                    }
                }
            }
        } catch (int v1_0) {
            this.mWriteLock.unlock();
            throw v1_0;
        }
        this.mWriteLock.unlock();
        if (this.mConfigure.mEnableBenchMarkIOSpeed > 0) {
            int v4 = this.testFileIOSpeed();
            Object[] v2 = new Object[1];
            v2[0] = Integer.valueOf(v4);
            String.format(java.util.Locale.US, "test io average speed:%d", v2);
            if (v4 > 0) {
                this.setIntValue(1508, v4);
            }
        }
        android.content.Context v0_12 = this.mStartCompleteListener;
        if (v0_12 != null) {
            v0_12.onStartComplete();
        }
        if ((this.mState == 1) && (this.mConfigure.mEnableCellularUp > 0)) {
            com.ss.mediakit.net.AVMDLMultiNetwork.alwayUpCellular(com.ss.mediakit.medialoader.AVMDLDataLoader.getApplicationContext());
        }
        com.ss.mediakit.net.AVMDLMultiNetwork.registerNetworkChangeCallback(com.ss.mediakit.medialoader.AVMDLDataLoader.getApplicationContext());
        return;
    }

/**
com.ss.mediakit.medialoader.AVMDLDataLoader;run()V
*/

    public void run()
    {
        this.this$0.startInternal();
        return;
    }


}