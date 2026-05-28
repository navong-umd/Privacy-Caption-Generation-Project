/*Application Package Name: org.fdroid.fdroid
class PRCS_30 {
/**
org.fdroid.fdroid.nearby.SwapService;onDestroy()V
*/

    public void onDestroy()
    {
        this.compositeDisposable.dispose();
        org.fdroid.fdroid.Utils.debugLog("SwapService", "Destroying service, will disable swapping if required, and unregister listeners.");
        org.fdroid.fdroid.Preferences.get().unregisterLocalRepoHttpsListeners(this.httpsEnabledListener);
        org.fdroid.fdroid.nearby.SwapService.localBroadcastManager.unregisterReceiver(this.onWifiChange);
        org.fdroid.fdroid.nearby.SwapService.localBroadcastManager.unregisterReceiver(this.bluetoothPeerFound);
        org.fdroid.fdroid.nearby.SwapService.localBroadcastManager.unregisterReceiver(this.bonjourPeerFound);
        org.fdroid.fdroid.nearby.SwapService.localBroadcastManager.unregisterReceiver(this.bonjourPeerRemoved);
        if (org.fdroid.fdroid.nearby.SwapService.bluetoothAdapter != null) {
            this.unregisterReceiver(this.bluetoothScanModeChanged);
        }
        org.fdroid.fdroid.nearby.BluetoothManager.stop(this);
        org.fdroid.fdroid.nearby.BonjourManager.stop(this);
        org.fdroid.fdroid.nearby.LocalHTTPDManager.stop(this);
        if (android.os.Build$VERSION.SDK_INT <= 28) {
            if ((org.fdroid.fdroid.nearby.SwapService.wifiManager != null) && (!org.fdroid.fdroid.nearby.SwapService.wasWifiEnabledBeforeSwap())) {
                org.fdroid.fdroid.nearby.SwapService.wifiManager.setWifiEnabled(0);
            }
            Exception v0_11 = cc.mvdan.accesspoint.WifiApControl.getInstance(this);
            if (v0_11 != null) {
                if (!org.fdroid.fdroid.nearby.SwapService.wasHotspotEnabledBeforeSwap()) {
                    v0_11.disable();
                } else {
                    v0_11.enable();
                }
            }
        }
        this.stopPollingConnectedSwapRepo();
        Exception v0_13 = this.timer;
        if (v0_13 != null) {
            v0_13.cancel();
        }
        androidx.core.app.ServiceCompat.stopForeground(this, 1);
        super.onDestroy();
        return;
    }


}