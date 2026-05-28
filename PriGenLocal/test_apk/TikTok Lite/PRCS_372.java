/*Application Package Name: com.tiktok.lite.go
class PRCS_372 {
/**
X.63L;LB()V
*/

    public final void LB()
    {
        int v1_0 = this;
        this.LD.L();
        if (!this.LFI) {
            this.LFFL.addCallback(this);
        } else {
            v1_0 = this.L(this.LFFL);
        }
        X.63I v0_4 = v1_0.LF;
        v0_4.LC = v1_0.LCI;
        try {
            if (X.63G.L(android.preference.PreferenceManager.getDefaultSharedPreferences(v0_4.LBL)) == X.63G.AUTO) {
                android.hardware.Sensor v6_0;
                android.hardware.SensorManager v10_1 = ((android.hardware.SensorManager) v0_4.LBL.getSystemService("sensor"));
                com.bytedance.helios.statichook.api.HeliosApiHook v5_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                Object[] v11 = new Object[1];
                v11[0] = Integer.valueOf(5);
                com.bytedance.helios.statichook.api.ExtraInfo v12_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(I)Landroid/hardware/Sensor;", "dzBzEhEpEcvSUUUuTBbKc9NnF3kueWo2KPq6bJnH0DffKli9z1VU1gTk4KCOSiCGslDDEl+7KA+TImt3+oXmuw==");
                com.bytedance.bpea.basics.Cert v2_3 = v5_1.preInvoke(100703, "android/hardware/SensorManager", "getDefaultSensor", v10_1, v11, "android.hardware.Sensor", v12_1);
                if (!v2_3.intercept) {
                    v6_0 = v10_1.getDefaultSensor(5);
                    v5_1.postInvoke(v6_0, 100703, "android/hardware/SensorManager", "getDefaultSensor", v10_1, v11, v12_1, 1);
                } else {
                    v5_1.postInvoke(0, 100703, "android/hardware/SensorManager", "getDefaultSensor", v10_1, v11, v12_1, 0);
                    v6_0 = ((android.hardware.Sensor) v2_3.returnValue);
                }
                v0_4.LCC = v6_0;
                if (v0_4.LCC != null) {
                    X.0a3.L(v10_1, v0_4, v0_4.LCC, 3, com.bytedance.bpea.basics.CertProviderManagerKt.findCert("bpea-lite_profile_scan_qrcode_close_ambient", 1509953538));
                }
            }
        } catch (X.0ZL) {
        }
        return;
    }

/**
com.ss.android.ugc.aweme.profile.qrcode.scan.SimpleQRCodeScanActivity;onResume()V
*/

    public final void onResume()
    {
        X.0xg.LB(this);
        super.onResume();
        X.63L v0 = this.LB;
        if (v0 != null) {
            v0.LB();
        }
        return;
    }


}