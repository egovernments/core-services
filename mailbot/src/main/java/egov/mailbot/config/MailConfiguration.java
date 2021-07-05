package egov.mailbot.config;

import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import egov.mailbot.models.MailProcessorConfig;
import egov.mailbot.service.TenantService;
import lombok.extern.slf4j.Slf4j;
import org.egov.tracer.model.CustomException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;

import javax.annotation.PostConstruct;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

@Configuration
@Slf4j
public class MailConfiguration {

    @Value("${config.repo.path}")
    private String configPaths;

    @Autowired
    private ResourceLoader resourceLoader;

    @Autowired
    private TenantService tenantService;

    @PostConstruct
    @Bean
    public Map<String, MailProcessorConfig> init() throws IOException {
        Map<String, MailProcessorConfig> mailProcessorConfigs = new HashMap<>();
        Map<String, String> errorMap = new HashMap<>();

        log.info("====================== EGOV MAIL PROCESSOR SERVICE ======================");
        log.info("LOADING CONFIGS: "+ configPaths);
        ObjectMapper mapper = new ObjectMapper(new YAMLFactory());

        String[] yamlUrls = configPaths.split(",");
        for (String configPath : yamlUrls) {
            try {
                log.info("Attempting to load config: "+configPath);
                Resource resource = resourceLoader.getResource(configPath);
                MailProcessorConfig config = mapper.readValue(resource.getInputStream(), MailProcessorConfig.class);
                config.setTenantIds(tenantService.getAllTenantIds(config.getService()));

                mailProcessorConfigs.put(config.getMailbox(), config);
            }
            catch (JsonParseException e){
                log.error("Failed to parse yaml file: " + configPath, e);
                errorMap.put("PARSE_FAILED", configPath);
            }
            catch (IOException e) {
                log.error("Exception while parsing service map for: " + configPath, e);
                errorMap.put("FAILED_TO_PARSE_FILE", configPath);
            }
        }

        if( !  errorMap.isEmpty())
            throw new CustomException(errorMap);
        else
            log.info("====================== CONFIGS LOADED SUCCESSFULLY! ====================== ");

        return mailProcessorConfigs;
    }


}
