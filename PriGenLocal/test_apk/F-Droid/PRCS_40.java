/*Application Package Name: org.fdroid.fdroid
class PRCS_40 {
/**
org.fdroid.fdroid.nearby.SwapWorkflowActivity;checkIfNewRepoOnSameWifi(Lorg/fdroid/fdroid/nearby/NewRepoConfig;)V
*/

    private void checkIfNewRepoOnSameWifi(org.fdroid.fdroid.nearby.NewRepoConfig p5)
    {
        if (!android.text.TextUtils.isEmpty(p5.getBssid())) {
            int v0_3 = ((android.net.wifi.WifiManager) androidx.core.content.ContextCompat.getSystemService(this.getApplicationContext(), android.net.wifi.WifiManager)).getConnectionInfo().getBSSID();
            if (!android.text.TextUtils.isEmpty(v0_3)) {
                int v1_1 = java.util.Locale.ENGLISH;
                if (!v0_3.toLowerCase(v1_1).equals(android.net.Uri.decode(p5.getBssid()).toLowerCase(v1_1))) {
                    Object[] v2_2 = new Object[1];
                    v2_2[0] = p5.getSsid();
                    android.widget.Toast.makeText(this, this.getString(org.fdroid.fdroid.R$string.not_on_same_wifi, v2_2), 1).show();
                }
            } else {
                return;
            }
        }
        return;
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