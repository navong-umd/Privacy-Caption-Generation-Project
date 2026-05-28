/*Application Package Name: com.tiktok.lite.go
class PRCS_358 {
/**
X.17v;L(LX/272; LX/17w;)V
*/

    public static final void L(X.272 p21, X.17w p22)
    {
        p21.LCC = p22;
        try {
            android.hardware.Sensor v8_0;
            android.hardware.SensorManager v1 = p21.LFFFF();
            X.17w v0_1 = p21.LCC;
            android.hardware.SensorManager v12 = p21.LFFFF();
            com.bytedance.helios.statichook.api.HeliosApiHook v7_0 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v13 = new Object[1];
            v13[0] = Integer.valueOf(1);
            com.bytedance.helios.statichook.api.ExtraInfo v14_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(I)Landroid/hardware/Sensor;", "dzBzEgAjS8/YVFkiQFyNY/5YsGxLrjrnefn6WvofFe5V4G8pD2FouL38wJ9kJLN/fA9lNKgE3gpdwq5KTNjMve5smkw3/PaPzS7YyNO4z6rm");
            com.bytedance.helios.statichook.api.Result v4_1 = v7_0.preInvoke(100703, "android/hardware/SensorManager", "getDefaultSensor", v12, v13, "android.hardware.Sensor", v14_1);
        } catch (Exception) {
            return;
        }
        if (!v4_1.intercept) {
            v8_0 = v12.getDefaultSensor(1);
            v7_0.postInvoke(v8_0, 100703, "android/hardware/SensorManager", "getDefaultSensor", v12, v13, v14_1, 1);
        } else {
            v7_0.postInvoke(0, 100703, "android/hardware/SensorManager", "getDefaultSensor", v12, v13, v14_1, 0);
            v8_0 = ((android.hardware.Sensor) v4_1.returnValue);
        }
        X.0a3.L(v1, v0_1, v8_0, 2, p21.LFFL().registerSensor());
        return;
    }

/**
X.272;LCI()V
*/

    public final void LCI()
    {
        this.LCCII = (this.LCCII + 1);
        X.18L v1_1 = this.LC.values().iterator();
        while (v1_1.hasNext()) {
            ((X.171) v1_1.next()).LCC();
        }
        X.17x.L(this, new X.26l());
        X.2hR v4_1 = new X.2hR(this);
        X.17w v0_6 = this.LB.LCCII.LB;
        if (v0_6 != null) {
            X.17w v0_7 = v0_6.values();
            if (v0_7 != null) {
                java.util.Iterator v5 = v0_7.iterator();
                while (v5.hasNext()) {
                    X.18L v1_0;
                    X.18A v3_1 = ((X.18A) v5.next());
                    X.17w v0_10 = v3_1.L;
                    if (v0_10 == null) {
                        X.17w v0_12 = v3_1.LB;
                        if (v0_12 != null) {
                            java.util.Iterator v2_1 = v0_12.iterator();
                            while (v2_1.hasNext()) {
                                X.17w v0_16 = ((X.185) v2_1.next()).LC;
                                if (v0_16 != null) {
                                    v1_0 = X.17v.L(v0_16);
                                    if (v1_0 == null) {
                                    }
                                }
                            }
                        }
                    } else {
                        java.util.Iterator v2_0 = v0_10.iterator();
                        while (v2_0.hasNext()) {
                            X.17w v0_20 = ((X.185) v2_0.next()).LC;
                            if (v0_20 != null) {
                                v1_0 = X.17v.L(v0_20);
                                if (v1_0 == null) {
                                }
                            }
                        }
                    }
                    X.17v.L(this, new X.17w(v1_0, v4_1));
                    break;
                }
            }
        }
        return;
    }


}