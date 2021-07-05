package egov.mailbot.service;

import egov.mailbot.config.MainConfiguration;
import net.minidev.json.JSONArray;
import org.egov.common.contract.request.RequestInfo;
import org.egov.mdms.model.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;

@Service
public class TenantService {

    @Autowired
    private MainConfiguration configuration;
    @Autowired
    private RestTemplate restTemplate;

    private String moduleName = "tenant";
    private String masterDetailsName = "citymodule";


    public Set<String> getAllTenantIds(String service) {

        String rootTenantId = configuration.getRootTenantId();
        String mdmsService = getMdmsService(service);
        String filter = "$.[?(@.module=='" + mdmsService +"')].tenants.*";

        MasterDetail masterDetail = MasterDetail.builder().name(masterDetailsName).filter(filter).build();
        ModuleDetail moduleDetail =
                ModuleDetail.builder().moduleName(moduleName).masterDetails(Collections.singletonList(masterDetail)).build();
        MdmsCriteria mdmsCriteria =
                MdmsCriteria.builder().tenantId(rootTenantId).moduleDetails(Collections.singletonList(moduleDetail)).build();

        MdmsCriteriaReq mdmsCriteriaReq = MdmsCriteriaReq.builder().mdmsCriteria(mdmsCriteria).requestInfo(RequestInfo.builder().build()).build();

        MdmsResponse mdmsResponse = restTemplate.postForObject(configuration.getMdmsHost() + configuration.getMdmsSearchPath(),
                mdmsCriteriaReq, MdmsResponse.class);

        Map<String, Map<String, JSONArray>> mdmsRes = mdmsResponse.getMdmsRes();

        JSONArray mdmsResValues = mdmsRes.get(moduleName).get(masterDetailsName);

        Set<String> tenantIds = new HashSet<>();

        for (Object mdmsResValue : mdmsResValues) {
            HashMap mdmsValue = (HashMap) mdmsResValue;
            String tenant = mdmsValue.get("code").toString();
            tenantIds.add(tenant);
        }

        return tenantIds;

    }

    private String getMdmsService(String service){
        return service.toUpperCase().replaceAll("-", "_");
    }
}
