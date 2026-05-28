/*Application Package Name: com.tiktok.lite.go
class PRCS_367 {
/**
X.7Or;<init>(Landroid/content/Context;)V
*/

    public 7Or(android.content.Context p23)
    {
        String v0_1 = ;
String v1_2 = new float[3];
        v0_1.L = v1_2;
        v0_1.LBL = new java.util.concurrent.CopyOnWriteArrayList();
        v0_1.LCCII = new X.7Op(v0_1);
        com.ss.android.vesdklite.log.LELogcat.Log(1, "Gyro", "init Gyro");
        if (p23 == null) {
            v0_1.LC = 0;
            v0_1.LCC = 0;
            com.ss.android.vesdklite.log.LELogcat.Log(4, "Gyro", "Gyro init failed, no context");
        } else {
            android.hardware.Sensor v7_0;
            android.hardware.SensorManager v11_1 = ((android.hardware.SensorManager) p23.getSystemService("sensor"));
            v0_1.LC = v11_1;
            com.bytedance.helios.statichook.api.HeliosApiHook v6_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v12 = new Object[1];
            v12[0] = Integer.valueOf(4);
            com.bytedance.helios.statichook.api.ExtraInfo v13_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(I)Landroid/hardware/Sensor;", "dzBzEhEpEcvSUUUuTBbKcGrIihcUpgr/zekQV0vUpk5UjJOtrlVH9kErtcEtHs+yqQ==");
            com.bytedance.helios.statichook.api.Result v3_2 = v6_1.preInvoke(100703, "android/hardware/SensorManager", "getDefaultSensor", v11_1, v12, "android.hardware.Sensor", v13_1);
            if (!v3_2.intercept) {
                v7_0 = v11_1.getDefaultSensor(4);
                v6_1.postInvoke(v7_0, 100703, "android/hardware/SensorManager", "getDefaultSensor", v11_1, v12, v13_1, 1);
            } else {
                v6_1.postInvoke(0, 100703, "android/hardware/SensorManager", "getDefaultSensor", v11_1, v12, v13_1, 0);
                v7_0 = ((android.hardware.Sensor) v3_2.returnValue);
            }
            v0_1.LCC = v7_0;
            if (v7_0 == null) {
                com.ss.android.vesdklite.log.LELogcat.Log(2, "Gyro", "focus mode x: the device does not support gyro");
                return;
            }
        }
        return;
    }

/**
X.7ud;<init>(Landroid/os/Handler; Landroid/content/Context;)V
*/

    public 7ud(android.os.Handler p6, android.content.Context p7)
    {
        this.LF = X.7P9.SESSION_STATE_IDLE;
        this.LFFFF = 1;
        this.LIILLLLZ = 1;
        this.LIILLZLL = 1065353216;
        this.LFI = new X.7PS(7, 30);
        this.LIILZLLZLZ = new java.util.concurrent.atomic.AtomicBoolean(0);
        this.LI = "camera2";
        this.LIILZZ = new X.7P5(this);
        this.LICI = new X.7ub(this);
        X.7uc v4_1 = new X.7uc(this);
        this.LIILZZL = v4_1;
        this.LIILZZLLZ = new X.7P6(this);
        this.LII = new X.7P7(this);
        this.LIILII = p6;
        this.L = p7;
        com.ss.android.vesdklite.log.LELogcat.Log(2, "LECameraHardware2Proxy", "getDeviceProxy, cameraType: ".concat(String.valueOf(X.7PZ.TYPE2)));
        this.LIILZ = new X.7PQ(v4_1);
        if (!com.ss.android.ugc.aweme.creativetool.nativeab.NativeABManagerAB.enable()) {
            this.LFFLLL = X.7LQ.L().L("velite_camera_exposure_compensation", 0);
            X.7PQ v1_4 = new StringBuilder("exposure comp = ");
            v1_4.append(this.LFFLLL);
            com.ss.android.vesdklite.log.LELogcat.Log(2, "LECamera2", v1_4.toString());
            X.7Nn.L("LECamera2", "velite_camera_type", Integer.valueOf(2));
        }
        X.7PQ v1_6 = this.LIILZ;
        this.LFLL = new X.7Or(p7);
        v1_6.LC = this.LFFFF();
        return;
    }

/**
X.7PF;LC()LX/7PB;
*/

    public final X.7PB LC()
    {
        X.87y v2_2;
        if (android.os.Build$VERSION.SDK_INT >= 24) {
            int v3 = X.7PC.L[this.LC.LC.ordinal()];
            if (v3 == 1) {
                com.ss.android.vesdklite.log.LELogcat.Log(2, "LECameraLite", "Create Camera2");
                v2_2 = new X.7ud(this.LB, this.LFFLLL);
            } else {
                if (v3 == 2) {
                    if (X.7Oy.L()) {
                        com.ss.android.vesdklite.log.LELogcat.Log(2, "LECameraLite", "Create TranssionCamera");
                        v2_2 = new X.87y(this.LB, this.LFFLLL);
                    } else {
                        com.ss.android.vesdklite.log.LELogcat.Log(4, "LECameraLite", "Transsion CamKit not supported, fallback to Camera2");
                        this.LC.LC = X.7PZ.TYPE2;
                        v2_2 = new X.7ud(this.LB, this.LFFLLL);
                    }
                } else {
                    com.ss.android.vesdklite.log.LELogcat.Log(2, "LECameraLite", "Create Camera1");
                    v2_2 = new X.7ua(this.LB, this.LFFLLL);
                }
            }
        } else {
            v2_2 = new X.7ua(this.LB, this.LFFLLL);
        }
        v2_2.LIII = this.LICI;
        v2_2.L(this.LFLL);
        return v2_2;
    }


}