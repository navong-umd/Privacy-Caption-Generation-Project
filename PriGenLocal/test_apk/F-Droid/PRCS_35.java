/*Application Package Name: org.fdroid.fdroid
class PRCS_35 {
/**
org.fdroid.fdroid.nearby.SwapWorkflowActivity;setupWifiAP()V
*/

    private void setupWifiAP()
    {
        String v0_0 = this.wifiApControl;
        if (v0_0 != null) {
            org.fdroid.fdroid.nearby.SwapService.putHotspotEnabledBeforeSwap(v0_0.isEnabled());
            if (android.os.Build$VERSION.SDK_INT <= 28) {
                this.wifiManager.setWifiEnabled(0);
            }
            try {
                if (!this.wifiApControl.enable()) {
                    android.widget.Toast.makeText(this, org.fdroid.fdroid.R$string.swap_toast_could_not_enable_hotspot, 1).show();
                    org.fdroid.fdroid.nearby.SwapService.putHotspotActivatedUserPreference(0);
                    android.util.Log.e("SwapWorkflowActivity", "Could not enable WiFi AP.");
                } else {
                    android.widget.Toast.makeText(this, org.fdroid.fdroid.R$string.swap_toast_hotspot_enabled, 0).show();
                    org.fdroid.fdroid.nearby.SwapService.putHotspotActivatedUserPreference(1);
                }
            } catch (String v0_4) {
                android.util.Log.e("SwapWorkflowActivity", "Error enabling WiFi: ", v0_4);
            }
            return;
        } else {
            android.util.Log.e("SwapWorkflowActivity", "WiFi AP is null");
            android.widget.Toast.makeText(this, org.fdroid.fdroid.R$string.swap_toast_could_not_enable_hotspot, 1).show();
            return;
        }
    }

/**
org.fdroid.fdroid.nearby.SwapWorkflowActivity;onActivityResult(I I Landroid/content/Intent;)V
*/

    public void onActivityResult(int p3, int p4, android.content.Intent p5)
    {
        super.onActivityResult(p3, p4, p5);
        int v5_2 = com.google.zxing.integration.android.IntentIntegrator.parseActivityResult(p3, p4, p5);
        if (v5_2 == 0) {
            if (p3 != 5) {
                if (p3 != 2) {
                    if (p3 != 3) {
                        if (p3 == 4) {
                            this.sendFDroidApk();
                        }
                    } else {
                        if (p4 == 0) {
                            org.fdroid.fdroid.Utils.debugLog("SwapWorkflowActivity", "User chose not to make Bluetooth discoverable, so doing nothing");
                            org.fdroid.fdroid.nearby.SwapService.putBluetoothVisibleUserPreference(0);
                        } else {
                            org.fdroid.fdroid.Utils.debugLog("SwapWorkflowActivity", "User made Bluetooth discoverable, will proceed to start bluetooth server.");
                            org.fdroid.fdroid.nearby.BluetoothManager.start(this);
                        }
                    }
                } else {
                    if (p4 != -1) {
                        org.fdroid.fdroid.Utils.debugLog("SwapWorkflowActivity", "User chose not to enable Bluetooth, so doing nothing");
                        org.fdroid.fdroid.nearby.SwapService.putBluetoothVisibleUserPreference(0);
                    } else {
                        org.fdroid.fdroid.Utils.debugLog("SwapWorkflowActivity", "User enabled Bluetooth, will make sure we are discoverable.");
                        this.ensureBluetoothDiscoverableThenStart();
                    }
                }
            } else {
                if (android.provider.Settings$System.canWrite(this)) {
                    this.setupWifiAP();
                }
            }
        } else {
            if (v5_2.getContents() != null) {
                String v3_9 = new org.fdroid.fdroid.nearby.NewRepoConfig(this, v5_2.getContents());
                if (!v3_9.isValidRepo()) {
                    android.widget.Toast.makeText(this, org.fdroid.fdroid.R$string.swap_qr_isnt_for_swap, 0).show();
                } else {
                    this.checkIfNewRepoOnSameWifi(v3_9);
                    this.confirmSwapConfig = v3_9;
                    this.showRelevantView();
                }
            }
        }
        return;
    }


}